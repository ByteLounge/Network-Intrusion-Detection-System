# NIDS — Network Intrusion Detection System (Open Source)

Overview
- This repository provides a lightweight Network Intrusion Detection System (NIDS) using free tools only: `tshark` for packet capture and `scikit-learn` for machine learning.
- Language: Python. Environment: VS Code (OS-agnostic).

Quick structure
- `data/raw/` — raw pcap files and external datasets
- `data/processed/` — CSVs and processed datasets
- `capture/` — scripts to capture and convert pcaps
- `ml/` — preprocessing, training, evaluation, and saved model
- `detection/` — real-time feature extraction and detector
- `logs/alerts.log` — detected intrusions

Prerequisites
- `tshark` (Wireshark CLI) installed and on PATH — used for capture and pcap→CSV conversion.
- Python 3.8+ and packages in `requirements.txt`:

Install

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r nids/requirements.txt
```

Capture live traffic (example)

```powershell
python nids/main.py capture --iface 1 --duration 60 --out nids/data/raw/capture1.pcap
```

Convert a pcap to CSV (tshark-based)

```powershell
python nids/main.py tocsv --pcap nids/data/raw/capture1.pcap --out nids/data/processed/capture1.csv
```

Train model (input: processed CSV with required features)

```powershell
python nids/main.py train --data nids/data/processed/train_features.csv --out nids/ml/model.pkl
```

Run live detection on a CSV

```powershell
python nids/main.py detect --csv nids/data/processed/capture1.csv
```

Notes
- The pipeline expects CSVs with fields used in feature extraction: `timestamp, src_ip, dst_ip, src_port, dst_port, protocol, length, tcp_flags`.
- You can use public datasets (NSL-KDD, CICIDS2017). Use `nids/ml/preprocess.py` as a helper to map fields into the required schema.

Security
- Model is trained locally. No external or paid services are used.
