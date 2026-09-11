"""Compatibility alias. Canonical B implementation: fleet_operator.workers.mesh."""
import sys
from fleet_operator.workers import mesh as _implementation
sys.modules[__name__] = _implementation
