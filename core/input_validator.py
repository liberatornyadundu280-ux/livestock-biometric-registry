import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image


_classifier = None
_weights = None
_transform = None
_bovine_keywords = {"ox", "water buffalo", "bison", "yak"}


def _get_classifier():
    global _classifier
    global _weights
    global _transform

    if _classifier is None:
        _weights = models.MobileNet_V2_Weights.DEFAULT
        _classifier = models.mobilenet_v2(weights=_weights)
        _classifier.eval()
        _transform = _weights.transforms()

    return _classifier, _weights, _transform


def _bovine_likelihood(image):
    classifier, weights, transform = _get_classifier()
    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        logits = classifier(image_tensor)
        probs = torch.softmax(logits, dim=1)[0]
        top_values, top_indices = torch.topk(probs, k=5)

    categories = weights.meta["categories"]
    top_labels = [categories[idx] for idx in top_indices.tolist()]
    top_scores = [float(v) for v in top_values.tolist()]

    bovine_score = 0.0
    for label, score in zip(top_labels, top_scores):
        label_lower = label.lower()
        if any(keyword in label_lower for keyword in _bovine_keywords):
            bovine_score = max(bovine_score, score)

    return bovine_score, top_labels


def validate_biometric_input(image_path):
    """
    Validate image quality and reject clearly non-cattle images.
    """
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception:
        return {
            "valid": False,
            "reason": "Could not open image file."
        }

    width, height = image.size
    if width < 96 or height < 96:
        return {
            "valid": False,
            "reason": "Image resolution too low. Use at least 96x96."
        }

    gray = np.array(image.convert("L"), dtype=np.float32)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))

    if brightness < 15 or brightness > 245:
        return {
            "valid": False,
            "reason": "Image lighting is too dark/bright."
        }

    if contrast < 10:
        return {
            "valid": False,
            "reason": "Image contrast is too low."
        }

    grad_y, grad_x = np.gradient(gray)
    sharpness = float(np.var(grad_x) + np.var(grad_y))
    if sharpness < 4:
        return {
            "valid": False,
            "reason": "Image looks blurry."
        }

    # Full-frame cattle-likeness check.
    bovine_score_full, top_labels_full = _bovine_likelihood(image)

    # Center crop check to better approximate muzzle-focused framing.
    crop_w = int(width * 0.6)
    crop_h = int(height * 0.6)
    left = (width - crop_w) // 2
    top = (height - crop_h) // 2
    center_crop = image.crop((left, top, left + crop_w, top + crop_h))
    bovine_score_center, top_labels_center = _bovine_likelihood(center_crop)

    bovine_score = max(bovine_score_full, bovine_score_center)
    warning = None
    if bovine_score < 0.08:
        warning = (
            "Image could not be confidently classified as cattle by heuristic model. "
            "Proceeding based on biometric similarity checks."
        )

    return {
        "valid": True,
        "warning": warning,
        "quality": {
            "brightness": brightness,
            "contrast": contrast,
            "sharpness": sharpness,
            "bovine_score": bovine_score
        },
        "top_labels": top_labels_full
    }
