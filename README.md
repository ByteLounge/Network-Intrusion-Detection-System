# NIDS

A lightweight Network Intrusion Detection System (NIDS) prototype implemented with free/open-source tools: Python, tshark (Wireshark), pandas and scikit-learn.

This repository provides a modular prototype for experimenting with packet capture → CSV conversion → feature extraction → machine learning detection pipelines. It includes a small CLI and a simple Tkinter GUI for convenience.

Key files:

- [nids/main.py](nids/main.py) — CLI entrypoint (capture, tocsv, preprocess, train, evaluate, detect)
- [nids/gui.py](nids/gui.py) — Basic Tkinter GUI to run core functions
- [nids/capture/pcap_to_csv.py](nids/capture/pcap_to_csv.py) — pcap → CSV using `tshark`
- [nids/detection/intrusion_detector.py](nids/detection/intrusion_detector.py) — detection runner and alerts logger
- [nids/ml/train_model.py](nids/ml/train_model.py) — training pipeline
- [nids/ml/evaluate_report.py](nids/ml/evaluate_report.py) — save classification report + confusion matrix

## Requirements

- Python 3.8+ (venv recommended)
- tshark (Wireshark) in PATH for live capture and pcap->CSV conversion
- Recommended Python packages in `requirements.txt`

Install Python deps (from repo root):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Install tshark:

- Windows: Install Wireshark and ensure `tshark.exe` is on your PATH.
- Linux/macOS: `sudo apt install tshark` or equivalent.

## Quick usage (CLI)

Preprocess NSL-KDD raw dataset (maps to simplified flow features):

```powershell
.venv\Scripts\python.exe nids\main.py preprocess data/raw/KDDTrain+.txt data/processed/nsl_kdd_train.csv --dataset nsl_kdd
```

Train a model (example — processed CSV -> model file):

```powershell
.venv\Scripts\python.exe nids\main.py train --data data/processed/nsl_kdd_train_binary.csv --out nids/ml/model_nsl_binary.pkl
```

Evaluate a saved model on a test CSV:

```powershell
.venv\Scripts\python.exe nids\main.py evaluate --data data/processed/nsl_kdd_test_binary.csv --model nids/ml/model_nsl_binary.pkl
```

Run detection (loads model, predicts, writes alerts to logs):

```powershell
.venv\Scripts\python.exe nids\main.py detect --csv data/processed/nsl_kdd_test.csv --model nids/ml/model_nsl_fixed.pkl
```

Generate saved evaluation report + confusion matrix (JSON / PNG):

```powershell
.venv\Scripts\python.exe nids\ml\evaluate_report.py --test data/processed/nsl_kdd_test_binary.csv --model nids/ml/model_nsl_binary.pkl
```

Convert pcap to CSV using tshark fields (example):

```powershell
.venv\Scripts\python.exe nids\main.py tocsv --pcap data/raw/capture.pcap --out data/processed/capture.csv
```

## GUI

There is a simple Tkinter GUI for running the pipeline interactively:

```powershell
.venv\Scripts\python.exe nids\gui.py
```

The GUI exposes buttons to preprocess, train, evaluate, detect and generate reports. It runs long tasks in background threads and writes brief output to the UI log area.

## Data

- Example dataset mapping/support for NSL-KDD is provided in `nids/ml/preprocess.py`. Put raw NSL-KDD files in `data/raw/` and use the `preprocess` command to map to `data/processed/`.
- For larger datasets (CICIDS2017) see `nids/cicids_handler.py` (scaffold) and adapt downloads/mapping as needed.

## Models, Reports & Logs

- Trained models are saved under `nids/ml/` (e.g. `model_nsl_binary.pkl`, `model_nsl_fixed.pkl`).
- Evaluation reports and confusion matrix images are saved to `nids/ml/reports/`.
- Detection alerts are appended to `nids/logs/alerts.log`.

## Notes & Tips

- The prototype uses a RandomForest classifier and simple flow-like features extracted from either tshark CSVs or mapped dataset rows (NSL-KDD mapping). Expect different performance depending on dataset and feature mapping.
- If you plan to perform live captures, ensure `tshark` is installed and you run with sufficient privileges to capture on the chosen interface.
- The code includes compatibility fallbacks for scikit-learn OneHotEncoder differences across versions.

## Contributing

This project is intended as an educational prototype. Feel free to open issues or make pull requests. Suggested improvements:

- More robust feature extraction from pcap/tshark output
- Support for streaming detection and lower-latency feature windows
- Dockerfile or Windows service wrapper for deployment

## UI

<img width="1000" height="843" alt="Screenshot 2026-01-22 145805" src="https://github.com/user-attachments/assets/57a3dadc-de09-43a8-87c8-fd26b01879ae" />


## License

MIT-style (no explicit license file included). Use and modify freely for experimentation.

---

If you'd like, I can also add a short `USAGE.md` with step-by-step screenshots for the GUI or a Dockerfile to containerize the environment.
