"""Prometheus HTTP metrics for the Flask API.

The deployed server is Flask's threaded development server (`python -m flask run`):
one process, many threads. Counters live in that process and are exposed on a
separate port. When gunicorn loads ``gunicorn.conf.py``, workers share a
multiprocess directory and the master serves the aggregated ``/metrics``.
"""

import logging
import os
import time
from urllib.parse import urlparse

from flask import request
from flask.globals import request_ctx
from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    multiprocess,
    start_http_server,
)
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.routing.exceptions import RequestRedirect

logger = logging.getLogger(__name__)

DEFAULT_SERVICE_NAME = "amara-backend"
DEFAULT_METRICS_PORT = 9091

# Set by gunicorn.conf before workers import this module. Not a user setting.
GUNICORN_METRICS_ENV = "AMARA_METRICS_GUNICORN"

# Shared with the other services. Do not rename or add labels.
REQUEST_DURATION_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1,
    2.5,
    5,
    10,
    30,
)

REQUESTS = Counter(
    "http_server_requests_total",
    "HTTP requests processed, partitioned by status and route template.",
    labelnames=("service", "method", "route", "status"),
)
DURATION = Histogram(
    "http_server_request_duration_seconds",
    "HTTP request latency in seconds, partitioned by status and route template.",
    labelnames=("service", "method", "route", "status"),
    buckets=REQUEST_DURATION_BUCKETS,
)
IN_FLIGHT = Gauge(
    "http_server_requests_in_flight",
    "HTTP requests currently being served.",
    labelnames=("service",),
    multiprocess_mode="livesum",
)

# Standard methods only. Anything else collapses to one series so a client
# cannot grow the metric set by inventing request-line tokens.
_KNOWN_METHODS = frozenset({
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
})
_OTHER_METHOD = "OTHER"

# Probes and the metrics scrape must not land in the API series.
_SKIP_PATHS = frozenset({
    "/metrics",
    "/_hc",
    "/health",
    "/healthz",
    "/ready",
    "/readyz",
    "/live",
    "/livez",
})

_START = "amara.metrics.start"
_SERVICE = "amara.metrics.service"
_TRACKED = "amara.metrics.tracked"
_DONE = "amara.metrics.done"

_httpd = None


def service_name():
    raw = os.environ.get("METRICS_SERVICE_NAME")
    if raw is None:
        return DEFAULT_SERVICE_NAME
    raw = raw.strip()
    return raw or DEFAULT_SERVICE_NAME


def resolve_metrics_port():
    """Return the metrics listen port, or None when exposure is disabled."""
    raw = os.environ.get("METRICS_PORT")
    if raw is None:
        return DEFAULT_METRICS_PORT
    raw = raw.strip()
    if raw in ("", "0"):
        return None
    try:
        port = int(raw)
    except ValueError as exc:
        raise ValueError(f"METRICS_PORT must be an integer, got {raw!r}") from exc
    if port == 0:
        return None
    if port < 1 or port > 65535:
        raise ValueError(f"METRICS_PORT out of range: {port}")
    return port


def _normalize_path(path):
    if path != "/" and path.endswith("/"):
        return path.rstrip("/")
    return path


def _should_skip(path):
    return _normalize_path(path) in _SKIP_PATHS


def _method_label(method):
    if isinstance(method, str):
        normalized = method.upper()
        if normalized in _KNOWN_METHODS:
            return normalized
    return _OTHER_METHOD


def route_template():
    """Flask route template, or ``unmatched`` when nothing matched.

    ``request.url_rule`` is unset for 404 and 405. A 405 still has a template;
    recover it by matching an allowed method. Redirects (strict slashes) use
    the destination template.
    """
    try:
        rule = request.url_rule
        if rule is not None and rule.rule:
            return rule.rule

        adapter = request_ctx.url_adapter
        if adapter is None:
            return "unmatched"

        exc = request.routing_exception
        if isinstance(exc, MethodNotAllowed) and exc.valid_methods:
            method = min(exc.valid_methods)
            matched, _ = adapter.match(method=method, return_rule=True)
            if matched is not None and matched.rule:
                return matched.rule

        if isinstance(exc, RequestRedirect) and exc.new_url:
            path = urlparse(exc.new_url).path or "/"
            matched, _ = adapter.match(path_info=path, return_rule=True)
            if matched is not None and matched.rule:
                return matched.rule
    except Exception:
        logger.debug("could not resolve route template", exc_info=True)
        return "unmatched"
    return "unmatched"


def _observe(status_code):
    if request.environ.get(_DONE) or not request.environ.get(_TRACKED):
        return
    request.environ[_DONE] = "1"
    service = request.environ.get(_SERVICE) or service_name()
    start = request.environ.get(_START)
    if start is None:
        elapsed = 0.0
    else:
        elapsed = max(0.0, time.perf_counter() - start)
    try:
        labels = {
            "service": service,
            "method": _method_label(request.method),
            "route": route_template(),
            "status": str(int(status_code)),
        }
        REQUESTS.labels(**labels).inc()
        DURATION.labels(**labels).observe(elapsed)
    finally:
        IN_FLIGHT.labels(service=service).dec()


def _before_request():
    try:
        if _should_skip(request.path):
            return
        service = service_name()
        started = time.perf_counter()
        IN_FLIGHT.labels(service=service).inc()
        request.environ[_SERVICE] = service
        request.environ[_START] = started
        request.environ[_TRACKED] = "1"
    except Exception:
        logger.exception("failed to start http request metrics")


def _after_request(response):
    try:
        _observe(response.status_code)
    except Exception:
        logger.exception("failed to record http request metrics")
    return response


def _teardown_request(exc):
    try:
        if request.environ.get(_DONE) or not request.environ.get(_TRACKED):
            return
        _observe(500)
    except Exception:
        logger.exception("failed to finish http request metrics")


_TRUE_FLAGS = {"1", "true", "t", "yes", "y", "on"}
_FALSE_FLAGS = {"", "0", "false", "f", "no", "n", "off"}


def _env_flag(name):
    raw = os.environ.get(name)
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in _TRUE_FLAGS:
        return True
    if value in _FALSE_FLAGS:
        return False
    return None


def _werkzeug_reloader_enabled():
    """Match Flask: reload follows ``FLASK_RUN_RELOAD``, otherwise ``FLASK_DEBUG``."""
    reload = _env_flag("FLASK_RUN_RELOAD")
    if reload is not None:
        return reload
    return _env_flag("FLASK_DEBUG") is True


def _reloader_parent():
    """True for the Werkzeug supervisor, which imports the app but does not serve.

    The serving child sets ``WERKZEUG_RUN_MAIN=true``. A process that is not
    using the reloader leaves that variable unset and must bind the port itself.
    """
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return False
    return _werkzeug_reloader_enabled()


def _scrape_registry():
    if os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return registry
    return REGISTRY


def start_metrics_server(port=None, *, from_gunicorn_master=False):
    """Serve ``/metrics`` on the internal metrics port.

    Gunicorn workers skip this; the master binds the port once from
    ``when_ready`` and is not treated as a Werkzeug reloader parent.
    An explicit ``port`` is for tests and ignores the reloader guard.
    """
    global _httpd
    if _httpd is not None:
        return _httpd

    in_gunicorn = os.environ.get(GUNICORN_METRICS_ENV) == "1"
    if in_gunicorn and not from_gunicorn_master:
        return None

    explicit_port = port is not None
    if not explicit_port and not from_gunicorn_master and _reloader_parent():
        return None
    if port is None:
        port = resolve_metrics_port()
        if port is None:
            return None

    registry = _scrape_registry()
    try:
        httpd, _thread = start_http_server(int(port), addr="0.0.0.0", registry=registry)
    except OSError:
        # Keep the API up if the metrics port is already taken.
        logger.exception("Prometheus metrics port %s is unavailable", port)
        return None
    _httpd = httpd
    logger.info("Prometheus metrics listening on :%s", httpd.server_address[1])
    return httpd


def init_http_metrics(app):
    """Record one sample per API request and start the metrics server."""
    if app.extensions.get("amara_http_metrics"):
        return
    app.extensions["amara_http_metrics"] = True
    app.before_request(_before_request)
    app.after_request(_after_request)
    app.teardown_request(_teardown_request)
    start_metrics_server()


def child_exit(server, worker):
    """Gunicorn ``child_exit`` hook. Drops dead workers from live gauges."""
    pid = getattr(worker, "pid", None)
    if not pid or not os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
        return
    multiprocess.mark_process_dead(pid)
