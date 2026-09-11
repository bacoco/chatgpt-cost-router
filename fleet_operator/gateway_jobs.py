"""Compatibility alias for the canonical typed gateway tool registrations."""
import sys
from . import gateway_tools as _implementation
sys.modules[__name__] = _implementation
