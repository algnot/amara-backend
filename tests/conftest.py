"""Keep test imports from binding the metrics port or reading Firebase secrets."""

import os
import sys
from unittest.mock import MagicMock

# Disable the metrics listener before app import. Tests that need the port
# start it explicitly.
os.environ["METRICS_PORT"] = "0"

_firebase = MagicMock()
sys.modules["firebase_admin"] = _firebase
sys.modules["firebase_admin.credentials"] = _firebase.credentials
sys.modules["firebase_admin.auth"] = _firebase.auth
