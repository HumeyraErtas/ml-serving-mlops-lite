from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

# TestClient, app import ederken settings okunur; bu yüzden env set edelim
def _prepare_model(tmp_dir: Path):
    # scripts/train_dummy_model.py 'models/1.0.0' yazar; testte tmp klasöre yönlendirelim
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])  # repo root
    # modeli repo root yerine tmp içine almak için çalışma dizinini tmp yapıyoruz
    subprocess.check_call([sys.executable, "scripts/train_dummy_model.py"], cwd=str(Path(__file__).resolve().parents[2]), env=env)


def test_healthz():
    # basit smoke
    from app.main import app
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.text == "ok"


def test_readyz_and_predict():
    # Model yoksa readyz 503 bekleriz
    os.environ["MODEL_DIR"] = "models"
    os.environ["MODEL_VERSION"] = "1.0.0"

    # modeli oluştur
    repo_root = Path(__file__).resolve().parents[2]
    subprocess.check_call([sys.executable, "scripts/train_dummy_model.py"], cwd=str(repo_root))

    from app.main import app
    client = TestClient(app)

    # startup event zaten load eder, ama TestClient bazen event’i ilk requestte tetikler
    r_ready = client.get("/readyz")
    assert r_ready.status_code == 200
    payload = r_ready.json()
    assert payload["status"] == "ready"
    assert payload["model_version"] == "1.0.0"

    r = client.post("/predict", json={"features": [0.1] * 12})
    assert r.status_code == 200
    out = r.json()
    assert out["model_version"] == "1.0.0"
    assert "score" in out
    assert "label" in out
