"""Preprocessing helpers for dataset mapping and cleaning."""
import pandas as pd
from pathlib import Path

# NSL-KDD column names (41 features + label)
nsl_columns = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land',
    'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
    'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
    'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count',
    'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
    'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
    'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label'
]


def map_nsl_kdd_to_flow(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    if 'protocol_type' in df.columns:
        out['protocol'] = df['protocol_type']
    if 'src_bytes' in df.columns:
        out['avg_pkt_len'] = df['src_bytes']
    if 'land' in df.columns:
        out['packet_count'] = df.get('num_outbound_cmds', 1)
    out['flow_duration'] = 0.0
    out['tcp_flags_agg'] = df.get('flag', '')
    out['label'] = df.get('label', df.iloc[:, -1])
    return out


def load_and_prepare(path: str, dataset_type: str = 'auto') -> pd.DataFrame:
    p = Path(path)
    # Try reading with header; if that fails, read without header (NSL-KDD raw)
    try:
        df = pd.read_csv(p)
    except Exception:
        df = pd.read_csv(p, header=None)

    if dataset_type == 'auto':
        if 'protocol_type' in df.columns:
            dataset_type = 'nsl-kdd'
        elif isinstance(df.columns, pd.RangeIndex) and df.shape[1] >= 40:
            dataset_type = 'nsl-kdd-raw'
        else:
            dataset_type = 'generic'

    # handle raw NSL-KDD without header by assigning known column names
    if dataset_type == 'nsl-kdd-raw':
        kdd_cols = [
            'duration','protocol_type','service','flag','src_bytes','dst_bytes','land','wrong_fragment','urgent',
            'hot','num_failed_logins','logged_in','num_compromised','root_shell','su_attempted','num_root',
            'num_file_creations','num_shells','num_access_files','num_outbound_cmds','is_host_login','is_guest_login',
            'count','srv_count','serror_rate','srv_serror_rate','rerror_rate','srv_rerror_rate','same_srv_rate',
            'diff_srv_rate','srv_diff_host_rate','dst_host_count','dst_host_srv_count','dst_host_same_srv_rate',
            'dst_host_diff_srv_rate','dst_host_same_src_port_rate','dst_host_srv_diff_host_rate','dst_host_serror_rate',
            'dst_host_srv_serror_rate','dst_host_rerror_rate','dst_host_srv_rerror_rate'
        ]
        if df.shape[1] >= len(kdd_cols) + 2:
            kdd_cols = kdd_cols + ['label','difficulty']
        elif df.shape[1] == len(kdd_cols) + 1:
            kdd_cols = kdd_cols + ['label']
        kdd_cols = kdd_cols[:df.shape[1]]
        df.columns = kdd_cols

    if dataset_type in ('nsl-kdd', 'nsl-kdd-raw'):
        return map_nsl_kdd_to_flow(df)
    return df


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('infile')
    p.add_argument('outfile')
    args = p.parse_args()
    df = load_and_prepare(args.infile)
    df.to_csv(args.outfile, index=False)
