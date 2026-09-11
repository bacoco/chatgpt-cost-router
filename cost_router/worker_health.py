"""Compatibility alias. Canonical B implementation: fleet_operator.workers.worker_health."""
import sys
from fleet_operator.workers import worker_health as _implementation
sys.modules[__name__] = _implementation
