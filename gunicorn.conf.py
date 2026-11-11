"""Gunicorn hooks for aggregated Prometheus metrics.

``run.sh`` starts Flask's single-process server, which does not load this
file. Load it with gunicorn (``gunicorn -c gunicorn.conf.py app:app``) so
every worker writes to one directory and the master serves ``/metrics``.
``PROMETHEUS_MULTIPROC_DIR`` has to be set before prometheus_client is
imported, which is why the directory is prepared above the import.
"""

import glob
import os
import tempfile

_multiproc_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR", "").strip()
if not _multiproc_dir:
    _multiproc_dir = tempfile.mkdtemp(prefix="prometheus-multiproc-")
    os.environ["PROMETHEUS_MULTIPROC_DIR"] = _multiproc_dir
else:
    os.makedirs(_multiproc_dir, exist_ok=True)
    for _db_file in glob.glob(os.path.join(_multiproc_dir, "*.db")):
        os.remove(_db_file)

# Workers inherit this and must not bind the metrics port themselves.
os.environ["AMARA_METRICS_GUNICORN"] = "1"

from util.metrics import child_exit as mark_worker_dead
from util.metrics import start_metrics_server

# Fork workers after this config is imported, not before the app is loaded
# in the master. Preload would share metric file state across processes.
preload_app = False


def when_ready(server):
    start_metrics_server(from_gunicorn_master=True)


def child_exit(server, worker):
    mark_worker_dead(server, worker)
