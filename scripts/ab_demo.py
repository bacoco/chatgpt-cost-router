#!/usr/bin/env python3
"""Explicit local demonstration: simulated A connectors and a real isolated B workspace."""
import argparse
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from operation_contracts.files import atomic_json
from chat_ops.config import configured
from fleet_operator.jobs.config import NodeConfig
from fleet_operator.jobs.service import Jobs


def prepare(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    resources = {
        "mail":{"connector":"gmail","account_ref":"demo-mail", "actions":["gmail.read","gmail.send"]},
        "repo":{"connector":"github","account_ref":"demo-git", "actions":["github.read","github.write"],
                "bindings":{"owner":"fixture","repo":"demo"}},
        "site":{"connector":"cowboy","account_ref":"demo-site", "actions":["cowboy.read","cowboy.publish"]}}
    projects = {"version":1,"projects":{"demo":{"members":["local-demo"], "resources":resources,
                "nodes":["demo-node"],"profiles":["plain-python"]}}}
    chat = {"version":1,"principal":"local-demo","projects_file":str(root/"projects.json"),
            "state_dir":str(root/"chat-state"),"surface":"chatgpt-web-chat","session":"simulated-connectors"}
    node = {"version":1,"node_id":"demo-node","principal":"local-demo", "projects_file":str(root/"projects.json"),
            "state_dir":str(root/"node-state"),"runtime_revision":"local-demo","max_concurrency":1,
            "profiles":{"plain-python":{"argv":[sys.executable,"-c",
            'from pathlib import Path; print(\'FLEET_PROGRESS {"current":1,"total":1}\'); Path("answer.txt").write_text("42"); print("Real local process, no model API")'],
            "isolation":"trusted-local","timeout_seconds":10,"max_output_bytes":4096,"artifacts":["answer.txt"]}}}
    workflow = {"version":1,"project_id":"demo","idempotency_key":"demo-four-app-steps", "deadline":time.time()+900,
        "steps":[{"id":"readmail","resource":"mail","action":"gmail.read","arguments":{"message_id":"fixture"}},
        {"id":"edit","resource":"repo","action":"github.write", "arguments":{"owner":"fixture","repo":"demo","content":{"$ref":"readmail.text"}},
         "verify":{"action":"github.read","arguments":{"owner":"fixture","repo":"demo"},"expect":{"verified":True}}},
        {"id":"publish","resource":"site","action":"cowboy.publish","arguments":{"text":{"$ref":"readmail.text"}},
         "verify":{"action":"cowboy.read","arguments":{},"expect":{"verified":True}}},
        {"id":"send","resource":"mail","action":"gmail.send","arguments":{"to":"fixture@example.invalid","body":{"$ref":"publish.url"}},
         "verify":{"action":"gmail.read","arguments":{"message_id":"fixture-sent"},"expect":{"verified":True}}}]}
    request = {"version":1,"project_id":"demo","idempotency_key":"demo-plain-process", "node_id":"demo-node",
               "profile":"plain-python","inputs":{},"deadline":time.time()+900}
    for name, data in {"projects":projects,"chat":chat,"node":node,"workflow":workflow,"request":request}.items():
        atomic_json(root/(name+".json"),data)
    return workflow, request, resources


class SimulatedConnectors:
    """Not a connector implementation or evidence of live Gmail/GitHub/Cowboy access."""
    def __init__(self):
        self.writes = []
    def invoke(self, invocation):
        if not invocation["read_only"]:
            self.writes.append(invocation["action"])
        return {"text":"Simulated connector content", "verified":True,
                "url":"https://example.invalid/simulated-publication"}


def execute(root):
    workflow, request, resources = prepare(root)
    root = Path(root)
    engine, _ = configured(root/"chat.json")
    now = time.time()
    for resource, binding in resources.items():
        for action in binding["actions"]:
            engine.capabilities.observe(engine.principal,"demo",resource,action,engine.surface,engine.session,
                {"level":"invocable","connector":binding["connector"],"account_ref":binding["account_ref"],
                 "tool_name":action,"observed_at":now,"expires_at":now+900,"evidence_ref":"SIMULATION_ONLY"})
    connectors = SimulatedConnectors()
    run = engine.submit(workflow)["run_id"]
    for _ in range(20):
        result = engine.run("demo",run,connectors)
        if result["state"] == "SUCCEEDED":
            break
        if result["state"] != "AWAITING_APPROVAL":
            raise RuntimeError("Unexpected demo A state: "+result["state"])
        engine.approve("demo",run,result["step"])
    else:
        raise RuntimeError("Demo A did not finish")
    jobs = Jobs(NodeConfig.from_file(root/"node.json"))
    job = jobs.submit(request)["run_id"]
    jobs.start("demo",job)
    until = time.monotonic()+15
    while time.monotonic() < until:
        status = jobs.status("demo",job)
        if status["state"] not in {"QUEUED","RUNNING","CANCELLING"}:
            break
        time.sleep(0.05)
    if status["state"] != "SUCCEEDED":
        raise RuntimeError("Demo B did not succeed: "+status["state"])
    return {"A":{"mode":"SIMULATED_CONNECTORS","state":result["state"],"write_actions":connectors.writes},
            "B":{"mode":"REAL_LOCAL_PROCESS","state":status["state"],"result":jobs.result("demo",job)},
            "live_external_side_effects":False,"model_api_calls":0,"directory":str(root.resolve())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory",required=True,help="new local directory; existing paths are refused")
    args = parser.parse_args()
    print(json.dumps(execute(args.directory),indent=2))


if __name__ == "__main__":
    main()
