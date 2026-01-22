"""Evaluate a saved model on a test CSV and print metrics."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score


def evaluate(test_csv, model_path):
    model = joblib.load(model_path)
    df = pd.read_csv(test_csv)
    if 'label' not in df.columns:
        raise ValueError('test CSV must include a `label` column')
    y = df['label']
    X = df.drop(columns=['label'])
    preds = model.predict(X)
    print('Accuracy:', accuracy_score(y, preds))
    print(classification_report(y, preds))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--data', required=True)
    p.add_argument('--model', required=True)
    args = p.parse_args()
    evaluate(args.data, args.model)
