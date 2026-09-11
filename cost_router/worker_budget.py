"""Compatibility alias. Canonical B implementation: fleet_operator.workers.worker_budget."""
import sys
from fleet_operator.workers import worker_budget as _implementation
sys.modules[__name__] = _implementation
