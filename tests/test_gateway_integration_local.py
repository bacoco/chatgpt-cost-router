"""Real local CLI gateway integration; MCP registrations checked with a recorder."""
import base64
import importlib.util
import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from operation_contracts.common import ContractError
from operation_contracts.files import atomic_json
from fleet_operator.core import FleetError
from fleet_operator.secure_gateway import configured_runner
from fleet_operator.remote_jobs import call
from fleet_operator.bounded_process import run
from fleet_operator.jobs.command import cleanup_container
import test_fleet_jobs as fixtures


class Recorder:
    def __init__(self):
        self.tools = {}
    def tool(self, **metadata):
        def register(fn):
            self.tools[fn.__name__] = fn
            return fn
        return register


class GatewayTests(unittest.TestCase):
    setUp = fixtures.ProcessTests.setUp
    tearDown = fixtures.ProcessTests.tearDown
    service = fixtures.ProcessTests.service
    request = fixtures.ProcessTests.request

    def gateway(self):
        service = self.service('from pathlib import Path; Path("answer.txt").write_text("42"); print("plain process")')
        path = self.root/"gateway.json"
        entry = Path(__file__).resolve().parents[1]/"scripts/fleet_jobs.py"
        runtime = {"python":sys.executable,"entrypoint":str(entry),"config":str(self.config_path),
                   "node_id":"node-a","runtime_revision":"unit-test-revision","policy_revision":service.config.revision}
        atomic_json(path,{"version":1,"max_output_bytes":262144,"hosts":{
            "local":{"transport":"local","allowed_roots":[str(self.root)],
                     "read_commands":["uname","git"],"write_commands":["git"],"runtime":runtime}}})
        return path, configured_runner(path)

    def test_typed_gateway_runs_process_and_retrieves_verified_artifact(self):
        _, runner = self.gateway()
        accepted = call(runner,"local","process_submit",{"request":self.request(),"start":True})
        args = {"project_id":"alpha","run_id":accepted["run_id"]}
        until = time.monotonic()+10
        while time.monotonic() < until:
            status = call(runner,"local","process_status",args)
            if status["state"] == "SUCCEEDED":
                break
            time.sleep(0.05)
        self.assertEqual(status["state"],"SUCCEEDED")
        artifact = call(runner,"local","process_artifact",{**args,"name":"answer.txt"})
        self.assertEqual(base64.b64decode(artifact["data"]),b"42")
        self.assertIn("plain process",call(runner,"local","process_logs",args)["text"])
        self.assertTrue(call(runner,"local","process_result",args)["receipt_digest"])
        self.assertEqual(call(runner,"local","process_list",{"project_id":"alpha"})["jobs"][0]["run_id"],args["run_id"])

    def test_project_spoofing_and_revision_mismatch_are_rejected(self):
        _, runner = self.gateway()
        with self.assertRaises(ContractError):
            call(runner,"local","process_profiles",{"project_id":"beta"})
        runner.runtime_bindings["local"]["runtime_revision"] = "not-the-installed-revision"
        with self.assertRaises(ContractError):
            call(runner,"local","node_health",{})

    def test_gateway_builder_registers_typed_jobs_not_unsafe_runner(self):
        path, _ = self.gateway()
        recorder = Recorder()
        with patch("fleet_operator.mcp_server.new_server",return_value=recorder), \
             patch("fleet_operator.mcp_server.annotations",return_value={}), \
             patch("fleet_operator.gateway_tools.annotations",return_value={}):
            from fleet_operator.mcp_server import build_server
            server = build_server(str(path))
        self.assertGreaterEqual(len(server.tools),20)
        self.assertEqual(server.tools["fleet_node_health"]("local")["node_id"],"node-a")
        with self.assertRaises(FleetError):
            server.tools["fleet_exec_write"]("local",["python3","-c","raise Exception()"])

    def test_relative_binary_and_git_escape_options_are_rejected(self):
        _, runner = self.gateway()
        for argv in (["./git","status"], ["git","diff","--no-index","/etc/passwd","/etc/group"],
                     ["git","-c","core.fsmonitor=evil","status"], ["git","status","--git-dir=/etc"]):
            with self.subTest(argv=argv), self.assertRaises(FleetError):
                runner.execute("local",argv,cwd=str(self.root),mode="read")

    def test_file_reader_does_not_follow_symlink_or_block_on_fifo(self):
        _, runner = self.gateway()
        outside = self.root.parent/"outside-fleet-fixture"
        link = self.root/"link"
        link.symlink_to(outside)
        os.mkfifo(self.root/"fifo",0o600)
        for path in (link,self.root/"fifo"):
            with self.subTest(path=path):
                result = runner.read_file("local",str(path),max_bytes=100)
                self.assertNotEqual(result["exit_code"],0)

    def test_process_capture_is_bounded_and_environment_is_clean(self):
        value = run([sys.executable,"-c",'print("x"*1000000)'],text=True,timeout=5,max_bytes=1024)
        self.assertLessEqual(len(value.stdout),1025)
        from fleet_operator.host_io import safe_environment
        self.assertNotIn("OPENAI_API_KEY",safe_environment({"OPENAI_API_KEY":"fixture", "PATH":"/bad"}))
        self.assertNotIn("PYTHONPATH",safe_environment({"PYTHONPATH":"/bad"}))

    def test_process_capture_timeout_is_bounded(self):
        started = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            run([sys.executable,"-c","import time; time.sleep(10)"],timeout=0.2,max_bytes=1024)
        self.assertLess(time.monotonic()-started,3)

    def test_container_cleanup_removes_only_owned_exact_id(self):
        profile = {"container":{"engine":"/usr/bin/podman"}}
        id_ = "a"*64
        (self.root/"container.cid").write_text(id_)
        with patch("subprocess.run",return_value=subprocess.CompletedProcess([],0)) as execute:
            self.assertTrue(cleanup_container(profile,self.root)["cleanup_verified"])
        self.assertEqual(execute.call_args.args[0],["/usr/bin/podman","rm","--force",id_])
        (self.root/"container.cid").write_text("--all")
        with self.assertRaises(ContractError):
            cleanup_container(profile,self.root)

    @unittest.skipUnless(importlib.util.find_spec("mcp"), "optional official mcp SDK unavailable in this environment")
    def test_actual_mcp_sdk_inprocess_discovery_and_health(self):
        import asyncio
        from mcp import Client
        from fleet_operator.mcp_server import build_server
        path, _ = self.gateway()
        async def check():
            async with Client(build_server(str(path)),raise_exceptions=True) as client:
                result = await client.list_tools()
                self.assertTrue(any(tool.name == "fleet_node_health" for tool in result.tools))
                output = await client.call_tool("fleet_node_health",{"host":"local"})
                self.assertFalse(output.is_error)
        asyncio.run(check())
