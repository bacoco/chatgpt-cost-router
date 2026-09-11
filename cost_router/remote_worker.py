"""Compatibility alias. Canonical B implementation: fleet_operator.workers.remote_worker."""
import sys
from fleet_operator.workers import remote_worker as _implementation
sys.modules[__name__] = _implementation
