"""Real-time intrusion detector: load model, extract features, predict, and log alerts."""
from pathlib import Path
import joblib
import pandas as pd
import time
from .feature_extraction import load_packet_csv, extract_flows


LOG = Path(__file__).parent.parent / "logs" / "alerts.log"
LOG.parent.mkdir(parents=True, exist_ok=True)


def run_detection(csv_path, model_path):
    print(f"Loading model from {model_path}")
    model = joblib.load(model_path)
    print(f"Reading packets CSV {csv_path}")
    pkt = load_packet_csv(csv_path)
    # If the CSV appears to have no header (columns are numeric strings), try dataset preprocessing
    col_names = [str(c) for c in pkt.columns]
    if all(c.isdigit() for c in col_names) or all(isinstance(c, int) for c in pkt.columns):
        try:
            from ..ml.preprocess import load_and_prepare
            print("Detected no-header CSV; running dataset preprocessor")
            flows = load_and_prepare(csv_path)
        except Exception:
            flows = pkt
    else:
    # if CSV already contains flow-level features, skip extraction
        if {'packet_count', 'flow_duration'}.issubset(set(pkt.columns)):
            flows = pkt
        else:
            flows = extract_flows(pkt)

    if flows.empty:
        print("No flows found in CSV.")
        return

    # prepare features for model pipeline: drop label if present
    X = flows.drop(columns=['label'], errors='ignore').fillna(0)

    preds = model.predict(X)
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(X)
    else:
        probs = None

    alerted = 0
    with open(LOG, "a", encoding="utf-8") as fh:
        for i, p in enumerate(preds):
            if str(p).lower() not in ("normal","benign","0"):
                # consider as attack
                line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} ALERT flow_index={i} prediction={p}"
                if probs is not None:
                    line += f" prob={probs[i].max():.3f}"
                fh.write(line + "\n")
                print("[WARNING] Intrusion detected:", line)
                alerted += 1

    print(f"Detection complete. Alerts written: {alerted} to {LOG}")
