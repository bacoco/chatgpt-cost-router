#!/usr/bin/env python3
"""Reproducible local validation; no deployment, model API or live connector calls."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cases, self.started = [], {}
    def startTest(self,test):
        self.started[test.id()] = time.monotonic()
        super().startTest(test)
    def record(self,test,state,detail=None):
        self.cases.append({"test":test.id(),"state":state,
                           "seconds":round(time.monotonic()-self.started.get(test.id(),time.monotonic()),6),
                           "detail":detail})
    def addSuccess(self,test):
        super().addSuccess(test)
        self.record(test,"PASS")
    def addSkip(self,test,reason):
        super().addSkip(test,reason)
        self.record(test,"SKIPPED",reason)
    def addFailure(self,test,err):
        super().addFailure(test,err)
        self.record(test,"FAIL",self._exc_info_to_string(err,test))
    def addError(self,test,err):
        super().addError(test,err)
        self.record(test,"ERROR",self._exc_info_to_string(err,test))
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        if err is not None:
            self.record(subtest,"SUBTEST_FAILURE",self._exc_info_to_string(err,test))


def inventory():
    result = {}
    for name in ("chat_ops","fleet_operator","operation_contracts","cost_router","tests","scripts","schemas","policy"):
        for file in sorted((ROOT/name).rglob("*")):
            if file.is_file() and "__pycache__" not in file.parts and file.suffix in {".py",".json",".sh"}:
                result[file.relative_to(ROOT).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True)
    args = parser.parse_args(argv)
    output = Path(args.output).resolve()
    output.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.environ.setdefault("TERM","dumb")
    before, started = inventory(), time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(ROOT/"tests"))
    with (output/"unittest.log").open("w") as log:
        result = unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
    packages = {}
    for name in ("jsonschema","mcp","setuptools","PyYAML"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "NOT_INSTALLED"
    after = inventory()
    report = {"version":1,"source_baseline":"cd897ddf3856ffdabef68ba1a71b43dd99efad46",
              "generated_at":datetime.now(timezone.utc).isoformat(),
              "python":sys.version,"platform":platform.platform(),"dependencies":packages,
              "tests_run":result.testsRun,"passed":sum(c["state"] == "PASS" for c in result.cases),
              "failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped),
              "successful":result.wasSuccessful() and before == after,"source_unchanged_during_tests":before == after,
              "seconds":round(time.monotonic()-started,6),"cases":result.cases,"source_sha256":after,
              "log_sha256":hashlib.sha256((output/"unittest.log").read_bytes()).hexdigest(),
              "live_gates":{"native_chat_attachment":"NOT_RUN","real_connectors":"NOT_RUN",
              "user_fleet_ssh":"NOT_RUN","macos_service_installation":"NOT_RUN","container_engine":"NOT_RUN",
              "remote_commit_merge":"NOT_PERFORMED"}}
    (output/"validation.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("tests_run","passed","failures","errors","skipped","successful","seconds")},indent=2))
    return 0 if report["successful"] else 1


if __name__ == "__main__":
    sys.exit(main())
