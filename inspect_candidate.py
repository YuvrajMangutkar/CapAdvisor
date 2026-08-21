import sys
sys.path.insert(0, 'backend')
import core.prediction_service as service
from ml.features import build_inference_features
from ml.predict import get_predictor

service._load_data()
cutoffs = service._cutoffs_df
branches = service._branches_df
colleges = service._colleges_df
c = int(cutoffs.iloc[0].college_id)
b = int(cutoffs.iloc[0].branch_id)
history = cutoffs.assign(
    nirf_rank_proxy=cutoffs.college_id.map(colleges.set_index('college_id').nirf_rank_proxy),
    demand_factor=cutoffs.branch_id.map(branches.set_index('branch_id').demand_factor),
)
features = build_inference_features(history, c, b, 'GOPENH', 1, 2026)
print('candidate', c, b, 'features', features)
print('prediction', get_predictor().predict(c, b, 'GOPENH', 2026, features))
