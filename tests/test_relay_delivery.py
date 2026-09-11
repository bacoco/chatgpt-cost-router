"""A lost GitHub publication must not repeat a machine operation."""
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from fleet_operator.relay import RelayConfig
from fleet_operator.relay_service import run_once
from fleet_operator.outbox import Outbox


class Bus:
    def __init__(self):
        self.path='.fleet/jobs/delivery-job-01.json'; self.sha='a'*64; self.published=[]; self.fail=True
        self.job={'version':1,'job_id':'delivery-job-01','host':'node','action':'process_submit',
                  'expires_at_unix':time.time()+300,'args':{'request':{}}}
    def fetch(self): pass
    def list_jobs(self): return [self.path]
    def read_job(self,path): return self.job,self.sha
    def push_result(self,job,result):
        if self.fail:
            self.fail=False; raise OSError('simulated lost publication')
        self.published.append(result); return 'fixture/result'


class RelayDeliveryTests(unittest.TestCase):
    def test_retry_publication_does_not_resubmit_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg=RelayConfig(Path(tmp),Path(tmp)/'config.json',state_dir=Path(tmp)/'state')
            bus=Bus()
            with patch('fleet_operator.relay_service.configured_runner',return_value=Mock()), \
                 patch('fleet_operator.relay_service.execute_job',return_value={'state':'RUNNING','run_id':'r'}) as execute:
                self.assertEqual(run_once(cfg,bus=bus)[0]['status'],'ACCEPTED')
                self.assertEqual(run_once(cfg,bus=bus)[0]['status'],'ACCEPTED')
                self.assertEqual(run_once(cfg,bus=bus),[])
                execute.assert_called_once()

    def test_interrupted_claim_is_uncertain_not_replayed(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg=RelayConfig(Path(tmp),Path(tmp)/'config.json',state_dir=Path(tmp)/'state')
            bus=Bus();bus.fail=False
            Outbox(cfg.state_dir).claim('delivery-job-01',bus.sha)
            with patch('fleet_operator.relay_service.configured_runner',return_value=Mock()), \
                 patch('fleet_operator.relay_service.execute_job') as execute:
                self.assertEqual(run_once(cfg,bus=bus)[0]['status'],'UNCERTAIN')
                execute.assert_not_called()

    def test_completed_failure_is_not_successful_submission(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg=RelayConfig(Path(tmp),Path(tmp)/'config.json',state_dir=Path(tmp)/'state')
            bus=Bus();bus.fail=False
            with patch('fleet_operator.relay_service.configured_runner',return_value=Mock()), \
                 patch('fleet_operator.relay_service.execute_job',return_value={'state':'FAILED','exit_code':7}):
                self.assertEqual(run_once(cfg,bus=bus)[0]['status'],'FAILED')
