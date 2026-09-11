"""Compatibility alias. Canonical B implementation: fleet_operator.workers.macos_launchd."""
import sys
from fleet_operator.workers import macos_launchd as _implementation
sys.modules[__name__] = _implementation
