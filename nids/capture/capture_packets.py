"""Capture packets using tshark CLI and save to pcap."""
import subprocess
import shlex
from pathlib import Path
import sys


def capture_to_pcap(iface, duration, out_path):
    """Capture for `duration` seconds on `iface` and save to out_path (pcap)."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = f"tshark -i {shlex.quote(str(iface))} -a duration:{int(duration)} -w {shlex.quote(str(out))}"
    print(f"Starting capture: {cmd}")
    try:
        subprocess.run(shlex.split(cmd), check=True)
        print(f"Capture saved to: {out}")
    except subprocess.CalledProcessError as e:
        print("tshark failed:", e, file=sys.stderr)
    except FileNotFoundError:
        print("tshark not found. Ensure Wireshark/tshark is installed and on PATH.")
