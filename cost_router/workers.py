"""Compatibility alias. Canonical B implementation: fleet_operator.workers.workers."""
import sys
from fleet_operator.workers import workers as _implementation
sys.modules[__name__] = _implementation
