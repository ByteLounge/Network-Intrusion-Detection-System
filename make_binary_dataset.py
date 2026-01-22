import pandas as pd

pairs = [
    ('data/processed/nsl_kdd_train.csv', 'data/processed/nsl_kdd_train_binary.csv', True),
    ('data/processed/nsl_kdd_test.csv',  'data/processed/nsl_kdd_test_binary.csv', False),
]

for inp, out, downsample in pairs:
    print('Loading', inp)
    df = pd.read_csv(inp)
    if 'label' not in df.columns:
        raise SystemExit('input missing label: ' + inp)
    df['label'] = df['label'].astype(str).str.strip()
    df['label'] = df['label'].apply(lambda v: 'normal' if v.lower() == 'normal' else 'attack')
    if downsample:
        attacks = df[df['label'] == 'attack']
        normals = df[df['label'] == 'normal']
        max_normals = min(len(normals), max(1000, len(attacks)*2))
        normals_sampled = normals.sample(n=max_normals, random_state=42)
        df2 = pd.concat([attacks, normals_sampled]).sample(frac=1.0, random_state=42).reset_index(drop=True)
        print(f'Original train rows={len(df)}, attacks={len(attacks)}, normals_sampled={len(normals_sampled)} -> {len(df2)}')
        df2.to_csv(out, index=False)
    else:
        print(f'Writing test binary rows={len(df)}')
        df.to_csv(out, index=False)
    print('Wrote', out)
