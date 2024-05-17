import os
import yaml
import mlflow
import mlflow.pytorch
from ultralytics import YOLO

# Set environment variables for DagsHub authentication
os.environ['MLFLOW_TRACKING_USERNAME'] = 'naziherrahel'
os.environ['MLFLOW_TRACKING_PASSWORD'] = '1b3e29ef364e14df28b5fa068b368eface00a055'

# Set MLflow tracking URI
mlflow.set_tracking_uri("https://dagshub.com/naziherrahel/Bachelor_project.mlflow")

# Debugging: Print environment variables and tracking URI
print("MLFLOW_TRACKING_URI:", mlflow.get_tracking_uri())
print("MLFLOW_TRACKING_USERNAME:", os.getenv('MLFLOW_TRACKING_USERNAME'))
print("MLFLOW_TRACKING_PASSWORD:", os.getenv('MLFLOW_TRACKING_PASSWORD'))

# Load parameters from params.yaml
with open(r"Research/params.yaml") as f:
    params = yaml.safe_load(f)

# Start an MLflow run
mlflow.start_run()

# Log parameters
mlflow.log_params(params)

# Load a pre-trained model
pre_trained_model = YOLO(params['model_type'])

# Train the model
model = pre_trained_model.train(
    data="./data.yaml",
    imgsz=params['imgsz'],
    batch=params['batch'],
    epochs=params['epochs'],
    optimizer=params['optimizer'],
    lr0=params['lr0'],
    seed=params['seed'],
    pretrained=params['pretrained'],
    name=params['name']
)

# Log metrics (assuming model.results is a dictionary of metrics)
if hasattr(model, 'results'):
    for key, value in model.results.items():
        mlflow.log_metric(key, value)

# Log the model artifact (e.g., model weights)
mlflow.pytorch.log_model(pre_trained_model, "model")

# End the MLflow run
mlflow.end_run()