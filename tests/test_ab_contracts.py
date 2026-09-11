import tempfile
import time
import unittest
from pathlib import Path
from operation_contracts.common import ContractError, loads, number
from operation_contracts.projects import Projects
from operation_contracts.journal import Journal
from operation_contracts.accounts import AccountBudgets


class ContractTests(unittest.TestCase):
    def test_duplicate_and_nonfinite_json_rejected(self):
        for text in ['{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}']:
            with self.subTest(text=text), self.assertRaises(ContractError):
                loads(text)
        with self.assertRaises(ContractError):
            number(True,0,10)

    def test_project_and_bound_resource(self):
        projects = Projects({"version":1,"projects":{"alpha":{"members":["alice"],"resources":{
            "repo":{"connector":"github","account_ref":"git-a","actions":["github.read"],
                    "bindings":{"owner":"example","repo":"alpha"}}}}}})
        projects.resource("alice","alpha","repo","github.read",{"owner":"example","repo":"alpha"})
        with self.assertRaises(ContractError):
            projects.project("bob","alpha")
        with self.assertRaises(ContractError):
            projects.resource("alice","alpha","repo","github.read",{"owner":"example","repo":"beta"})

    def test_bad_grants_are_rejected(self):
        for members in [[{}],True,[],["alice","alice"]]:
            with self.subTest(members=members), self.assertRaises(ContractError):
                Projects({"version":1,"projects":{"a":{"members":members}}})

    def test_journal_idempotency_scope_and_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            j = Journal(Path(td)/"journal.db")
            a, created = j.register("alice","alpha","process","same",{"a":1},"policy")
            b, duplicate = j.register("alice","alpha","process","same",{"a":1},"policy")
            self.assertTrue(created)
            self.assertFalse(duplicate)
            self.assertEqual(a["id"],b["id"])
            with self.assertRaises(ContractError):
                j.register("alice","alpha","process","same",{"a":2},"policy")
            c, _ = j.register("alice","beta","process","same",{"a":1},"policy")
            self.assertNotEqual(a["id"],c["id"])
            with self.assertRaises(ContractError):
                j.get("bob","alpha",a["id"])
            self.assertTrue(j.transition(a["id"],{"QUEUED"},"RUNNING",{"token":"owner"}))
            self.assertFalse(j.transition(a["id"],{"QUEUED"},"RUNNING"))
            self.assertFalse(j.transition(a["id"],{"RUNNING"},"SUCCEEDED",token="wrong"))
            self.assertTrue(j.transition(a["id"],{"RUNNING"},"SUCCEEDED",token="owner"))

    def test_account_budget_is_shared_not_per_project(self):
        with tempfile.TemporaryDirectory() as td:
            budgets = AccountBudgets(Journal(Path(td)/"journal.db"))
            with self.assertRaises(ContractError):
                budgets.reserve("account-A","project-a-job",3)
            budgets.observe("account-A",5,time.time()+60,"operator-limit")
            budgets.reserve("account-A","project-a-job",3)
            with self.assertRaises(ContractError):
                budgets.reserve("account-A","project-b-job",3)
            budgets.settle("account-A","project-a-job",2)
            budgets.reserve("account-A","project-b-job",3)
            self.assertEqual(budgets.status("account-A")["remaining_units"],0)
            with self.assertRaises(ContractError):
                budgets.settle("account-A","project-a-job",1)
