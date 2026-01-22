from nids.ml.preprocess import load_and_prepare

pairs = [
    ('data/raw/KDDTrain+.txt','data/processed/nsl_kdd_train.csv'),
    ('data/raw/KDDTest+.txt','data/processed/nsl_kdd_test.csv')
]
for inp, out in pairs:
    print('Processing', inp, '->', out)
    df = load_and_prepare(inp, dataset_type='nsl-kdd-raw')
    print('Shape:', df.shape, 'Columns:', list(df.columns)[:10])
    df.to_csv(out, index=False)
    print('Wrote', out)
