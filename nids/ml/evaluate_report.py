import joblib
import pandas as pd
import json
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

MODEL_PATH = Path(__file__).parent / 'model_nsl_binary.pkl'
REPORT_DIR = Path(__file__).parent / 'reports'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def run_report(test_csv, model_path=None):
    model_path = Path(model_path) if model_path else MODEL_PATH
    print('Loading model from', model_path)
    model = joblib.load(model_path)
    df = pd.read_csv(test_csv)
    if 'label' not in df.columns:
        raise SystemExit('Test CSV must contain `label` column')
    y_true = df['label']
    X = df.drop(columns=['label'])

    y_pred = model.predict(X)

    # classification report
    creport = classification_report(y_true, y_pred, output_dict=True)
    report_txt = classification_report(y_true, y_pred)
    (REPORT_DIR / 'classification_report.txt').write_text(report_txt, encoding='utf-8')
    (REPORT_DIR / 'classification_report.json').write_text(json.dumps(creport, indent=2), encoding='utf-8')
    print('Wrote classification report to', REPORT_DIR)

    # confusion matrix
    labels = sorted(list(set(y_true) | set(y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    cm_df.to_csv(REPORT_DIR / 'confusion_matrix.csv')

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(len(labels)), yticks=np.arange(len(labels)),
           xticklabels=labels, yticklabels=labels,
           ylabel='True label', xlabel='Predicted label', title='Confusion Matrix')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

    # annotate
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'), ha='center', va='center',
                    color='white' if cm[i, j] > thresh else 'black')

    plt.tight_layout()
    out_png = REPORT_DIR / 'confusion_matrix.png'
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    print('Wrote confusion matrix to', out_png)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--test', required=True)
    p.add_argument('--model', required=False)
    args = p.parse_args()
    run_report(args.test, args.model)
