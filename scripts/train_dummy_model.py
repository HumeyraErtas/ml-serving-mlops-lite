from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score


@dataclass
class Meta:
    model_type: str
    trained_at_utc: str
    n_features: int
    auc: float
    threshold: float


def main():
    version = "1.0.0"
    out_dir = Path("models") / version
    out_dir.mkdir(parents=True, exist_ok=True)

    X, y = make_classification(
        n_samples=8000,
        n_features=12,
        n_informative=6,
        n_redundant=2,
        weights=[0.93, 0.07],
        random_state=42,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=200, n_jobs=None)
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    auc = float(roc_auc_score(y_test, proba))

    meta = Meta(
        model_type="LogisticRegression",
        trained_at_utc=datetime.now(timezone.utc).isoformat(),
        n_features=X.shape[1],
        auc=auc,
        threshold=0.5,
    )

    joblib.dump(model, out_dir / "model.joblib")
    (out_dir / "meta.json").write_text(json.dumps(asdict(meta), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved model to: {out_dir}")
    print(f"AUC: {auc:.4f}")


if __name__ == "__main__":
    main()
