import joblib
import pprint

m = joblib.load('nids/ml/model_nsl.pkl')
print('MODEL TYPE:', type(m))
try:
    names = list(m.named_steps.keys())
    print('PIPELINE STEPS:', names)
except Exception:
    print('No named_steps on model')

from sklearn.compose import ColumnTransformer
for name, step in getattr(m, 'named_steps', {}).items():
    print('\nSTEP:', name, 'TYPE:', type(step))
    if isinstance(step, ColumnTransformer):
        print('FOUND ColumnTransformer:\n', step)
        try:
            print('FEATURE NAMES OUT:')
            print(step.get_feature_names_out())
        except Exception as e:
            print('get_feature_names_out error:', e)

# If pipeline has a preprocessor attribute, try to inspect
if hasattr(m, 'named_steps'):
    for nm, st in m.named_steps.items():
        try:
            print('\nComponent:', nm)
            pprint.pprint(st)
        except Exception:
            pass
print('\nDone')
