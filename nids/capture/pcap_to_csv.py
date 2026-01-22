"""Use tshark to export pcap packets to CSV with fields useful for ML."""
import subprocess
import shlex
from pathlib import Path
import sys


def pcap_to_csv(pcap_path, out_csv):
    pcap = Path(pcap_path)
    out = Path(out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "frame.time_epoch",
        "ip.src",
        "ip.dst",
        "ip.proto",
        "tcp.srcport",
        "tcp.dstport",
        "udp.srcport",
        "udp.dstport",
        "frame.len",
        "tcp.flags",
    ]

    tshark_fields = " ".join([f"-e {f}" for f in fields])
    cmd = f"tshark -r {shlex.quote(str(pcap))} -T fields {tshark_fields} -E header=y -E separator=,"

    try:
        print(f"Running: {cmd}")
        res = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        text = res.stdout.decode(errors="ignore")
        with open(out, "w", newline="", encoding="utf-8") as fh:
            fh.write(text)
        print(f"CSV exported to {out}")
    except subprocess.CalledProcessError as e:
        print("tshark failed:", e.stderr.decode(), file=sys.stderr)
    except FileNotFoundError:
        print("tshark not found. Ensure Wireshark/tshark is installed and on PATH.")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("pcap")
    p.add_argument("out")
    args = p.parse_args()
    pcap_to_csv(args.pcap, args.out)
