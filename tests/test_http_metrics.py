import os
import shutil
import socket
import subprocess
import sys
import urllib.request

from prometheus_client import REGISTRY, generate_latest

from app import app
from util.metrics import (
    DURATION,
    GUNICORN_METRICS_ENV,
    IN_FLIGHT,
    REQUEST_DURATION_BUCKETS,
    resolve_metrics_port,
    service_name,
    start_metrics_server,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_PROBE = {}


def _probe_user(**kwargs):
    _PROBE["in_flight"] = REGISTRY.get_sample_value(
        "http_server_requests_in_flight",
        {"service": service_name()},
    )
    _PROBE["path"] = kwargs.get("id")
    return "ok"


def _probe_boom(**kwargs):
    del kwargs
    raise RuntimeError("boom")


def _probe_ok(**kwargs):
    del kwargs
    return "ok"


if "metrics_probe_user" not in app.view_functions:
    app.add_url_rule(
        "/users/<int:id>",
        endpoint="metrics_probe_user",
        view_func=_probe_user,
        methods=["GET"],
    )
if "metrics_probe_boom" not in app.view_functions:
    app.add_url_rule(
        "/metrics-test/boom/<int:id>",
        endpoint="metrics_probe_boom",
        view_func=_probe_boom,
        methods=["GET"],
    )
if "metrics_probe_slash" not in app.view_functions:
    app.add_url_rule(
        "/metrics-test/slash/",
        endpoint="metrics_probe_slash",
        view_func=_probe_ok,
        methods=["GET"],
    )


def _counter(route, status, method="GET", service=None):
    return REGISTRY.get_sample_value(
        "http_server_requests_total",
        {
            "service": service or service_name(),
            "method": method,
            "route": route,
            "status": status,
        },
    )


def _free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def test_route_label_is_template():
    template = "/users/<int:id>"
    labels_status = "200"
    before = _counter(template, labels_status) or 0
    before_duration = REGISTRY.get_sample_value(
        "http_server_request_duration_seconds_count",
        {
            "service": "amara-backend",
            "method": "GET",
            "route": template,
            "status": labels_status,
        },
    ) or 0
    in_flight_before = REGISTRY.get_sample_value(
        "http_server_requests_in_flight",
        {"service": "amara-backend"},
    ) or 0

    response = app.test_client().get("/users/42?verbose=1")

    assert response.status_code == 200
    assert _PROBE["path"] == 42
    assert _PROBE["in_flight"] == in_flight_before + 1
    assert _counter(template, labels_status) == before + 1
    assert REGISTRY.get_sample_value(
        "http_server_request_duration_seconds_count",
        {
            "service": "amara-backend",
            "method": "GET",
            "route": template,
            "status": labels_status,
        },
    ) == before_duration + 1
    assert _counter("/users/42", labels_status) is None
    assert REGISTRY.get_sample_value(
        "http_server_requests_in_flight",
        {"service": "amara-backend"},
    ) == in_flight_before

    payload = generate_latest(REGISTRY).decode()
    assert 'route="/users/<int:id>"' in payload
    assert 'route="/users/42"' not in payload


def test_blueprint_route_label_includes_prefix_not_raw_path():
    template = "/user/get/<string:user_id>"
    before = _counter(template, "403") or 0

    response = app.test_client().get("/user/get/12345")

    assert response.status_code == 403
    assert response.get_json()["message"] == "Authorization token missing"
    assert _counter(template, "403") == before + 1
    assert _counter("/user/get/12345", "403") is None


def test_unmatched_route_label():
    before = _counter("unmatched", "404") or 0
    response = app.test_client().get("/no-such-route")
    assert response.status_code == 404
    assert _counter("unmatched", "404") == before + 1


def test_unknown_method_is_a_single_label():
    raw_method = "X" * 80
    before = _counter("unmatched", "404", method="OTHER") or 0
    response = app.test_client().open("/no-such-route", method=raw_method)
    assert response.status_code == 404
    assert _counter("unmatched", "404", method="OTHER") == before + 1
    assert _counter("unmatched", "404", method=raw_method) is None

    template = "/users/<int:id>"
    before_route = _counter(template, "405", method="OTHER") or 0
    routed = app.test_client().open("/users/42", method="NOPE")
    assert routed.status_code == 405
    assert _counter(template, "405", method="OTHER") == before_route + 1
    assert _counter(template, "405", method="NOPE") is None
    payload = generate_latest(REGISTRY).decode()
    assert raw_method not in payload
    assert 'method="NOPE"' not in payload


def test_method_not_allowed_keeps_route_template():
    template = "/users/<int:id>"
    before = _counter(template, "405", method="POST") or 0
    response = app.test_client().post("/users/42")
    assert response.status_code == 405
    assert _counter(template, "405", method="POST") == before + 1
    assert _counter("unmatched", "405", method="POST") is None


def test_redirect_uses_destination_template():
    template = "/metrics-test/slash/"
    before = _counter(template, "308") or 0
    response = app.test_client().get("/metrics-test/slash")
    assert response.status_code == 308
    assert _counter(template, "308") == before + 1
    assert _counter("unmatched", "308") is None


def test_unhandled_error_keeps_route_template():
    template = "/metrics-test/boom/<int:id>"
    before = _counter(template, "500") or 0
    response = app.test_client().get("/metrics-test/boom/7")
    assert response.status_code == 500
    assert _counter(template, "500") == before + 1


def test_health_and_metrics_paths_are_not_recorded():
    health_before = _counter("/_hc", "200")
    unmatched_before = _counter("unmatched", "404") or 0
    metrics_before = _counter("/metrics", "404")

    health = app.test_client().get("/_hc")
    missing_metrics = app.test_client().get("/metrics")

    assert health.status_code == 200
    assert health.get_json() == {"status": "server is running"}
    assert missing_metrics.status_code == 404
    assert "/metrics" not in {rule.rule for rule in app.url_map.iter_rules()}
    assert _counter("/_hc", "200") == health_before
    assert _counter("/metrics", "404") == metrics_before
    assert (_counter("unmatched", "404") or 0) == unmatched_before


def test_histogram_buckets_match_contract():
    assert DURATION._upper_bounds == [*REQUEST_DURATION_BUCKETS, float("inf")]
    assert IN_FLIGHT._labelnames == ("service",)
    assert DURATION._labelnames == ("service", "method", "route", "status")


def test_service_name_env(monkeypatch):
    monkeypatch.setenv("METRICS_SERVICE_NAME", "billing-api")
    template = "/users/<int:id>"
    before = _counter(template, "200", service="billing-api") or 0
    response = app.test_client().get("/users/9")
    assert response.status_code == 200
    assert _counter(template, "200", service="billing-api") == before + 1
    monkeypatch.setenv("METRICS_SERVICE_NAME", "  ")
    assert service_name() == "amara-backend"


def test_metrics_port_disabled(monkeypatch):
    monkeypatch.setenv("METRICS_PORT", "")
    assert resolve_metrics_port() is None
    monkeypatch.setenv("METRICS_PORT", "0")
    assert resolve_metrics_port() is None
    monkeypatch.delenv("METRICS_PORT")
    assert resolve_metrics_port() == 9091


def test_metrics_server_exposes_route_template_on_its_own_port():
    port = _free_port()
    httpd = start_metrics_server(port=port)
    assert httpd is not None
    host, bound_port = httpd.server_address[:2]
    if host in ("0.0.0.0", ""):
        host = "127.0.0.1"
    elif host == "::":
        host = "[::1]"
    try:
        app.test_client().get("/users/42")
        url = f"http://{host}:{bound_port}/metrics"
        with urllib.request.urlopen(url, timeout=5) as resp:
            assert resp.status == 200
            body = resp.read().decode()
        assert "http_server_requests_total" in body
        assert "http_server_request_duration_seconds" in body
        assert "http_server_requests_in_flight" in body
        assert 'route="/users/<int:id>"' in body
        assert 'route="/users/42"' not in body
        assert 'le="0.005"' in body
        assert 'le="30.0"' in body
        assert 'le="+Inf"' in body
    finally:
        httpd.shutdown()


def test_child_exit_marks_worker_gauge_dead(tmp_path):
    script = r"""
import glob
import os
import sys

os.environ["PROMETHEUS_MULTIPROC_DIR"] = sys.argv[1]
from util.metrics import IN_FLIGHT, child_exit

class Worker:
    pid = os.getpid()

IN_FLIGHT.labels(service="amara-backend").set(2)
pattern = os.path.join(sys.argv[1], f"gauge_livesum_{Worker.pid}.db")
assert glob.glob(pattern), os.listdir(sys.argv[1])
child_exit(None, Worker())
assert glob.glob(pattern) == []
"""
    subprocess.check_call([sys.executable, "-c", script, str(tmp_path)], cwd=ROOT)


def test_gunicorn_config_enables_multiprocess_before_import():
    script = r"""
import importlib.util
import os

spec = importlib.util.spec_from_file_location("gconf", "gunicorn.conf.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from prometheus_client import values
from util.metrics import GUNICORN_METRICS_ENV

path = os.environ["PROMETHEUS_MULTIPROC_DIR"]
assert os.path.isdir(path), path
assert os.environ[GUNICORN_METRICS_ENV] == "1"
assert values.ValueClass._multiprocess is True
assert callable(mod.child_exit)
assert callable(mod.when_ready)
assert mod.preload_app is False
print(path)
"""
    env = os.environ.copy()
    env.pop("PROMETHEUS_MULTIPROC_DIR", None)
    env.pop(GUNICORN_METRICS_ENV, None)
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr or completed.stdout)
    path = completed.stdout.strip().splitlines()[-1]
    shutil.rmtree(path, ignore_errors=True)
