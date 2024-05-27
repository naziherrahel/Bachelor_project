import torch

def export_model(model_path, export_path):
    model = torch.load(model_path)
    model.export(format='onnx', path=export_path)

if __name__ == "__main__":
    model_path = 'models/best.pt'
    export_path = 'models/deployed_model.onnx'
    export_model(model_path, export_path)
