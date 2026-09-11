"""MCP SDK transport settings regression fixtures; no external service or account."""
import unittest
from types import SimpleNamespace
from pydantic import BaseModel, ConfigDict
from operation_contracts.mcp_runtime import serve


class SDKStartupTests(unittest.TestCase):
    def test_v2_has_settings_but_http_configuration_is_passed_to_run(self):
        class V2Settings(BaseModel):
            model_config = ConfigDict(extra='forbid',validate_assignment=True)
            debug: bool = False
        class V2:
            settings = V2Settings()
            def run(self,**kwargs): self.called = kwargs
        server = V2()
        serve(lambda _:server,['--config','fixture','--transport','streamable-http','--port','8822'])
        self.assertEqual(server.called,{'transport':'streamable-http','host':'127.0.0.1','port':8822,
            'streamable_http_path':'/mcp','stateless_http':True,'json_response':True})
        self.assertEqual(server.settings.model_dump(),{'debug':False})

    def test_v1_existing_transport_settings_remain_compatible(self):
        class V1:
            settings = SimpleNamespace(host='localhost',port=8000,stateless_http=False,
                                       json_response=False,streamable_http_path='/old')
            def run(self,transport): self.called = transport
        server = V1()
        serve(lambda _:server,['--config','fixture','--transport','streamable-http','--port','8822'])
        self.assertEqual(server.called,'streamable-http')
        self.assertEqual(server.settings.host,'127.0.0.1')
        self.assertEqual(server.settings.port,8822)
        self.assertEqual(server.settings.streamable_http_path,'/mcp')
        self.assertTrue(server.settings.json_response and server.settings.stateless_http)

    def test_stdio_does_not_attempt_http_configuration(self):
        class Stdio:
            def run(self,transport): self.called = transport
        server = Stdio()
        serve(lambda _:server,['--config','fixture'])
        self.assertEqual(server.called,'stdio')
