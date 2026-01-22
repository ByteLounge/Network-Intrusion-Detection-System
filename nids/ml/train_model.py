"""Train a Random Forest classifier on processed flow features and save model."""
from pathlib import Path
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def train(csv_path, out_model_path):
    df = pd.read_csv(csv_path, header=0)

    # If label column missing, try to infer: NSL-KDD raw files have label as second-to-last
    if 'label' not in df.columns:
        if df.shape[1] >= 2:
            # assume last column is difficulty, second-last is label
            df.rename(columns={df.columns[-2]: 'label'}, inplace=True)
        else:
            raise ValueError('Input CSV must contain a `label` column or be NSL-KDD raw with label column')

    # features: use numeric columns; categorical: protocol, tcp_flags_agg
    y = df['label']
    X = df.drop(columns=['label'])

    numeric_cols = X.select_dtypes(include=['number']).columns.tolist()
    cat_cols = [c for c in X.columns if c not in numeric_cols]

    numeric_transformer = StandardScaler()
    try:
        categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse=False)
    except TypeError:
        # scikit-learn 1.2+ uses 'sparse_output' instead of 'sparse'
        categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, cat_cols),
        ]
    )

    clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    pipe = Pipeline(steps=[('pre', preprocessor), ('clf', clf)])

    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    except ValueError:
        # fallback for very small or imbalanced synthetic datasets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print('Training model...')
    pipe.fit(X_train, y_train)
    print('Training complete. Evaluating on test set...')
    preds = pipe.predict(X_test)
    print(classification_report(y_test, preds))

    outp = Path(out_model_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, outp)
    print(f'Model saved to {outp}')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--data', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()
    train(args.data, args.out)
