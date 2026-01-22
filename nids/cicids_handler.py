"""CICIDS2017 helper: downloader scaffold and CSV-to-flow mapper."""
import pandas as pd
from pathlib import Path


def map_cicids_csv_to_flow(in_csv, out_csv):
    p = Path(in_csv)
    df = pd.read_csv(p)
    out = pd.DataFrame()
    if 'Flow Duration' in df.columns:
        out['flow_duration'] = df['Flow Duration']
    if 'Total Fwd Packets' in df.columns and 'Total Backward Packets' in df.columns:
        out['packet_count'] = df['Total Fwd Packets'] + df['Total Backward Packets']
    if 'Total Length of Fwd Packets' in df.columns and 'Total Length of Bwd Packets' in df.columns:
        total_len = df['Total Length of Fwd Packets'].fillna(0) + df['Total Length of Bwd Packets'].fillna(0)
        out['avg_pkt_len'] = total_len / out['packet_count'].replace({0:1})
    if 'Protocol' in df.columns:
        out['protocol'] = df['Protocol']
    for c in ['Label','Flow ID','attack_label']:
        if c in df.columns:
            out['label'] = df[c]
            break
    out.to_csv(out_csv, index=False)
    print('Mapped', in_csv, '->', out_csv)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='CICIDS helper')
    p.add_argument('--map', nargs=2, help='in_csv out_csv')
    args = p.parse_args()
    if args.map:
        map_cicids_csv_to_flow(args.map[0], args.map[1])
