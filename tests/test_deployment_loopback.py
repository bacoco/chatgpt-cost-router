"""A localhost MCP verification must not go through an ambient network proxy."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

class LoopbackTests(unittest.TestCase):
    def test_rpc_explicitly_disables_proxy_only_for_loopback(self):
        path=Path(__file__).resolve().parents[1]/'scripts/ab_gateway_activate.py'
        spec=importlib.util.spec_from_file_location('test_gateway_activation',path)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        response=MagicMock(); response.__enter__.return_value.read.return_value=json.dumps({'result':{'ok':True}}).encode()
        with patch.object(module,'ProxyHandler') as proxy, patch.object(module,'build_opener') as factory:
            factory.return_value.open.return_value=response
            self.assertEqual(module.rpc(8812,'tools/list',{}),{'ok':True})
            proxy.assert_called_once_with({})
            request=factory.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url,'http://127.0.0.1:8812/mcp')
