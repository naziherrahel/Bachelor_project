import os
import yaml
import mlflow
import mlflow.pytorch
from ultralytics import YOLO
from getpass import getpass
import dagshub

dagshub.init('Bachelor_project', 'naziherrahel', mlflow= True)

# Set up DagsHub environment variables
os.environ['MLFLOW_TRACKING_USERNAME'] = input('Enter your DagsHub username: ')
os.environ['MLFLOW_TRACKING_PASSWORD'] = getpass('Enter your DagsHub access token: ')
os.environ['MLFLOW_TRACKING_PROJECTNAME'] = input('Enter your DagsHub project name: ')

# Debugging: Print environment variables and tracking URI
print("MLFLOW_TRACKING_URI:", mlflow.get_tracking_uri())
print("MLFLOW_TRACKING_USERNAME:", os.getenv('MLFLOW_TRACKING_USERNAME'))
print("MLFLOW_TRACKING_PASSWORD:", os.getenv('MLFLOW_TRACKING_PASSWORD'))


mlflow.set_tracking_uri(f'https://dagshub.com/{os.environ["MLFLOW_TRACKING_USERNAME"]}/{os.environ["MLFLOW_TRACKING_PROJECTNAME"]}.mlflow')

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