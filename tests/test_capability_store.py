"""Synthetic account/context evidence; no connector or account access."""
import tempfile
import unittest
from pathlib import Path

from chat_ops.capability_store import CapabilityStore
from operation_contracts.common import ContractError, canonical
from operation_contracts.journal import Journal


class CapabilityStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.journal = Journal(Path(self.tmp.name) / "evidence.sqlite3")
        self.store = CapabilityStore(self.journal)
        self.context = ("alice", "alpha", "repo", "github.read", "codex-cli", "session-one")

    def evidence(self, account="account-a", connector="github", observed=1000, level="invocable"):
        return {"level":level, "tool_name":"fixture.read", "connector":connector,
                "account_ref":account, "observed_at":observed, "expires_at":observed+60,
                "evidence_ref":"synthetic-discovery"}

    def observe(self, evidence):
        self.store.observe(*self.context, evidence, now=1005)

    def require(self, account="account-a", connector="github", context=None, now=1005):
        return self.store.require(*(context or self.context),
                                  {"connector":connector, "account_ref":account}, now=now)

    def test_newer_other_account_survives_reopen_without_clobbering(self):
        first, second = self.evidence(), self.evidence("account-b", observed=1001)
        self.observe(first)
        self.observe(second)
        self.store = CapabilityStore(self.journal)
        self.assertEqual(self.require(), first)
        self.assertEqual(self.require("account-b"), second)

    def test_same_timestamp_accounts_and_connectors_coexist(self):
        for connector, account in (("github", "account-a"), ("github", "account-b"), ("other", "account-a")):
            self.observe(self.evidence(account, connector))
        for connector, account in (("github", "account-a"), ("github", "account-b"), ("other", "account-a")):
            with self.subTest(connector=connector, account=account):
                self.assertEqual(self.require(account, connector), self.evidence(account, connector))

    def test_wrong_account_or_connector_has_no_evidence(self):
        self.observe(self.evidence())
        for connector, account in (("github", "account-b"), ("other", "account-a")):
            with self.subTest(connector=connector, account=account), self.assertRaises(ContractError):
                self.require(account, connector)

    def test_same_account_conflict_and_stale_observation_still_rejected(self):
        first = self.evidence(observed=1001)
        self.observe(first)
        self.observe(first)  # identical observations remain idempotent
        for evidence in (self.evidence(observed=1001, level="denied"), self.evidence()):
            with self.subTest(evidence=evidence), self.assertRaises(ContractError):
                self.observe(evidence)
        self.assertEqual(self.require(), first)

    def test_denial_and_expiry_remain_account_scoped(self):
        self.observe(self.evidence())
        self.observe(self.evidence("account-b", observed=1001, level="denied"))
        self.assertEqual(self.require()["level"], "invocable")
        with self.assertRaises(ContractError):
            self.require("account-b")
        with self.assertRaises(ContractError):
            self.require(now=1060)

    def test_every_existing_context_dimension_still_isolated(self):
        self.observe(self.evidence())
        for index, value in enumerate(("bob", "beta", "mail", "github.search", "service", "session-two")):
            context = list(self.context)
            context[index] = value
            with self.subTest(index=index), self.assertRaises(ContractError):
                self.require(context=context)

    def test_legacy_six_field_keys_are_retained_but_require_fresh_observation(self):
        legacy_key, evidence = canonical(list(self.context)), self.evidence()
        with self.journal.transaction() as db:
            db.execute("INSERT INTO connector_evidence VALUES(?,?,?)",
                       (legacy_key, evidence["observed_at"], canonical(evidence)))
        self.store = CapabilityStore(self.journal)
        with self.assertRaises(ContractError):
            self.require()
        self.observe(evidence)
        self.store = CapabilityStore(self.journal)
        self.assertEqual(self.require(), evidence)
        with self.journal.transaction() as db:
            rows = db.execute("SELECT scope,data FROM connector_evidence").fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(next(row["data"] for row in rows if row["scope"] == legacy_key), canonical(evidence))
