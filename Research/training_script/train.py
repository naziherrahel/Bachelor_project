# import yaml
# from ultralytics import YOLO


# with open(r"Research/params.yaml") as f:
#     params = yaml.safe_load(f)

# # load a pre-trained model 
# pre_trained_model = YOLO(params['model_type'])

# # train 
# model = pre_trained_model.train(
#     data="C:/Users/Администратор/Desktop/dust_detection_project/data.yaml",
#     imgsz=params['imgsz'],
#     batch=params['batch'],
#     epochs=params['epochs'],
#     optimizer=params['optimizer'],
#     lr0=params['lr0'],
#     seed=params['seed'],
#     pretrained=params['pretrained'],
#     name=params['name']
# )

import yaml
import mlflow
import mlflow.pytorch
from ultralytics import YOLO

# Set MLflow tracking URI
mlflow.set_tracking_uri("https://dagshub.com/<your-username>/<your-repo-name>.mlflow")

# Load parameters from params.yaml
with open("Research/params.yaml") as f:
    params = yaml.safe_load(f)

# Start an MLflow run
mlflow.start_run()

# Log parameters
mlflow.log_params(params)

# Load a pre-trained model
pre_trained_model = YOLO(params['model_type'])

# Train the model
model = pre_trained_model.train(
    data="C:/Users/Администратор/Desktop/dust_detection_project/data.yaml",  # Update this path as necessary
    img_size=params['imgsz'],
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
