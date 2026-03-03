import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import torch.nn.functional as F

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load pretrained MobileNetV2
base_model = models.mobilenet_v2(pretrained=True)

# Remove classifier
embedding_model = nn.Sequential(*list(base_model.children())[:-1])
embedding_model.eval()
embedding_model.to(device)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def get_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        embedding = embedding_model(image)
    
    embedding = embedding.view(embedding.size(0), -1)
    
    # Normalize embedding
    embedding = F.normalize(embedding, p=2, dim=1)
    
    return embedding

def cosine_similarity(emb1, emb2):
    return F.cosine_similarity(emb1, emb2).item()

def compare_images(img1_path, img2_path, threshold=0.7):
    emb1 = get_embedding(img1_path)
    emb2 = get_embedding(img2_path)
    
    similarity = cosine_similarity(emb1, emb2)
    
    print("\n===== Biometric Verification Result =====")
    print(f"Cosine Similarity Score: {similarity:.4f}")
    print(f"Decision Threshold: {threshold}")
    
    if similarity > threshold:
        print("Result: VERIFIED (Same Animal)")
    else:
        print("Result: NOT VERIFIED (Different Animal)")
    print("=========================================\n")
    
if __name__ == "__main__":
    image1 = "images/image1.jpg"
    image2 = "images/image2.jpg"
    
    compare_images(image1, image2)