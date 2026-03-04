import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import torch.nn.functional as F

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load MobileNetV2 (updated syntax)
weights = models.MobileNet_V2_Weights.DEFAULT
base_model = models.mobilenet_v2(weights=weights)

# Remove classifier
embedding_model = nn.Sequential(*list(base_model.children())[:-1])
embedding_model.eval()
embedding_model.to(device)

# Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def get_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        features = embedding_model(image)  # shape: [1, 1280, 7, 7]

        # Global Average Pooling
        features = torch.mean(features, dim=[2, 3])  # shape: [1, 1280]

        # L2 normalization
        features = F.normalize(features, p=2, dim=1)

    return features.squeeze().cpu().numpy()  # shape: (1280,)


def get_embedding_list(image_path):
    embedding = get_embedding(image_path)
    return embedding.squeeze().tolist()