#!/usr/bin/env python3
"""Main CLI for NIDS: capture, convert, train, evaluate, detect."""
import argparse
from pathlib import Path

ROOT = Path(__file__).parent

def main():
    parser = argparse.ArgumentParser(description="NIDS CLI")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("capture", help="Capture live traffic to pcap using tshark")
    p.add_argument("--iface", required=True, help="Interface index or name for tshark")
    p.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    p.add_argument("--out", default=str(ROOT / "data" / "raw" / "capture.pcap"))

    p2 = sub.add_parser("tocsv", help="Convert pcap to csv using tshark fields")
    p2.add_argument("--pcap", required=True)
    p2.add_argument("--out", default=str(ROOT / "data" / "processed" / "capture.csv"))

    p3 = sub.add_parser("train", help="Train model from processed CSV")
    p3.add_argument("--data", required=True)
    p3.add_argument("--out", default=str(ROOT / "ml" / "model.pkl"))

    p4 = sub.add_parser("evaluate", help="Evaluate model on test CSV")
    p4.add_argument("--data", required=True)
    p4.add_argument("--model", default=str(ROOT / "ml" / "model.pkl"))

    p5 = sub.add_parser("detect", help="Run intrusion detection on CSV")
    p5.add_argument("--csv", required=True)
    p5.add_argument("--model", default=str(ROOT / "ml" / "model.pkl"))

    p6 = sub.add_parser("preprocess", help="Preprocess dataset CSV")
    p6.add_argument("input")
    p6.add_argument("output")
    p6.add_argument("--dataset", default="auto")

    args = parser.parse_args()
    if args.cmd == "capture":
        from capture.capture_packets import capture_to_pcap
        capture_to_pcap(args.iface, args.duration, args.out)
    elif args.cmd == "tocsv":
        from capture.pcap_to_csv import pcap_to_csv
        pcap_to_csv(args.pcap, args.out)
    elif args.cmd == "train":
        from ml.train_model import train
        train(args.data, args.out)
    elif args.cmd == "evaluate":
        from ml.evaluate_model import evaluate
        evaluate(args.data, args.model)
    elif args.cmd == "detect":
        from detection.intrusion_detector import run_detection
        run_detection(args.csv, args.model)
    elif args.cmd == "preprocess":
        from ml.preprocess import load_and_prepare
        df = load_and_prepare(args.input, dataset_type=args.dataset)
        df.to_csv(args.output, index=False)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
