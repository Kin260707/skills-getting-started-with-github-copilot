import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest


def test_app_starts_and_serves_activities():
    repo_root = Path(__file__).resolve().parents[1]
    app_path = repo_root / "src" / "app.py"
    port = "8010"

    env = os.environ.copy()
    env["PORT"] = port

    process = subprocess.Popen(
        [sys.executable, str(app_path)],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    try:
        deadline = time.time() + 10
        while time.time() < deadline:
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                pytest.fail(f"Server exited early with output:\n{output}")

            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/activities", timeout=1) as response:
                    assert response.status == 200
                    return
            except Exception:
                time.sleep(0.2)

        pytest.fail("Server did not become ready in time")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(5)
            except subprocess.TimeoutExpired:
                process.kill()


def test_unregister_endpoint_removes_participant():
    repo_root = Path(__file__).resolve().parents[1]
    app_path = repo_root / "src" / "app.py"
    port = "8011"

    env = os.environ.copy()
    env["PORT"] = port

    process = subprocess.Popen(
        [sys.executable, str(app_path)],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    try:
        deadline = time.time() + 10
        while time.time() < deadline:
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                pytest.fail(f"Server exited early with output:\n{output}")

            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/activities", timeout=1) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(0.2)
        else:
            pytest.fail("Server did not become ready in time")

        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/activities/Chess%20Club/signup?email=michael@mergington.edu",
            method="DELETE",
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            assert response.status == 200
            body = json.loads(response.read().decode())
            assert "Unregistered" in body["message"]
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(5)
            except subprocess.TimeoutExpired:
                process.kill()
