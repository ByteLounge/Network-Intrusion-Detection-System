"""Feature extraction utilities: convert packet-level CSV into flow features."""
from pathlib import Path
import pandas as pd
import numpy as np


def load_packet_csv(csv_path):
    # Attempt to load standard tshark output columns
    df = pd.read_csv(csv_path, low_memory=False)
    return df


def extract_flows(packet_df, time_col="frame.time_epoch"):
    """Group packets into flows and compute features.

    Flow key: src_ip, dst_ip, src_port, dst_port, protocol
    Computes: flow_duration, packet_count, avg_packet_len, tcp_flags_agg
    """
    df = packet_df.copy()
    # normalize column names
    for c in df.columns:
        if "." in c:
            df.rename(columns={c: c.replace('.', '_')}, inplace=True)

    # expected columns
    timestamp = time_col.replace('.', '_') if '.' in time_col else time_col
    ts = timestamp if timestamp in df.columns else df.columns[0]

    # create normalized columns if present
    df.columns = [c.replace('.', '_') for c in df.columns]

    # determine port columns
    def choose(col1, col2):
        if col1 in df.columns:
            return col1
        if col2 in df.columns:
            return col2
        return None

    s_port = choose('tcp_srcport', 'udp_srcport')
    d_port = choose('tcp_dstport', 'udp_dstport')

    # fill NaNs
    if ts not in df.columns:
        df[ts] = 0.0
    df[ts] = pd.to_numeric(df[ts], errors='coerce').fillna(0.0)

    # Build flow key
    keys = []
    if 'ip_src' in df.columns and 'ip_dst' in df.columns and s_port and d_port and 'ip_proto' in df.columns:
        keys = ['ip_src','ip_dst', s_port, d_port, 'ip_proto']
    else:
        # fallback: group by src,dst,proto
        keys = [c for c in ['ip_src','ip_dst','ip_proto'] if c in df.columns]

    # If no grouping keys are available, this may already be a flow-level dataset
    if not keys:
        # Try to map NSL-KDD style rows to flow features using the preprocessing mapper
        try:
            from ..ml.preprocess import map_nsl_kdd_to_flow
            mapped = map_nsl_kdd_to_flow(df)
            return mapped
        except Exception:
            # As a last resort, treat each row as a single flow
            rows = []
            for _, row in df.iterrows():
                rec = {}
                rec['packet_count'] = int(row.get('count', 1)) if pd.notna(row.get('count', None)) else 1
                rec['flow_duration'] = float(row.get('duration', 0.0)) if pd.notna(row.get('duration', None)) else 0.0
                if 'src_bytes' in df.columns and 'dst_bytes' in df.columns and rec['packet_count']:
                    try:
                        rec['avg_pkt_len'] = (float(row.get('src_bytes', 0)) + float(row.get('dst_bytes', 0))) / max(rec['packet_count'], 1)
                    except Exception:
                        rec['avg_pkt_len'] = 0.0
                else:
                    rec['avg_pkt_len'] = 0.0
                rec['tcp_flags_agg'] = row.get('tcp_flags', '') if 'tcp_flags' in df.columns else ''
                if 'label' in df.columns:
                    rec['label'] = row.get('label')
                rows.append(rec)
            return pd.DataFrame(rows)

    grouped = df.groupby(keys)

    rows = []
    for name, g in grouped:
        rec = {}
        if isinstance(name, tuple):
            for i,k in enumerate(keys):
                rec[k] = name[i]
        else:
            rec[keys[0]] = name
        rec['packet_count'] = len(g)
        rec['flow_duration'] = g[ts].max() - g[ts].min() if len(g)>1 else 0.0
        # average length
        if 'frame_len' in g.columns:
            rec['avg_pkt_len'] = pd.to_numeric(g['frame_len'], errors='coerce').fillna(0).astype(float).mean()
        else:
            rec['avg_pkt_len'] = 0.0
        # flags aggregate
        if 'tcp_flags' in g.columns:
            rec['tcp_flags_agg'] = ";".join(sorted(set(g['tcp_flags'].astype(str).fillna(''))))
        else:
            rec['tcp_flags_agg'] = ''
        rows.append(rec)

    feat = pd.DataFrame(rows)
    return feat


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("out")
    args = p.parse_args()
    df = load_packet_csv(args.csv)
    feats = extract_flows(df)
    feats.to_csv(args.out, index=False)
