import tensorflow as tf
import numpy as np
from PIL import Image
import json
from pathlib import Path
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "plant_disease_mnv2.keras"
LABELS_PATH = BASE_DIR / "labels.json"

# loads the model
model = tf.keras.models.load_model(MODEL_PATH)

# Load labels
with open(LABELS_PATH) as f:
    labels_dict = json.load(f)
labels = [labels_dict[str(i)] if str(i) in labels_dict else v for i, v in labels_dict.items()]

def predict_image(file_path):
    img = Image.open(file_path).convert("RGB")
    # resise the image to 224, 224. 
    img = img.resize((224, 224))
    x = np.array(img)[None, ...].astype("float32")
    x = preprocess_input(x)

    preds = model.predict(x)[0]
    idx = int(np.argmax(preds))
    confidence = float(preds[idx])
    label = labels[idx]

    # Gets the top three predictions based on confidence
    top3 = [
        {"label": labels[i], "confidence": float(preds[i])}
        for i in np.argsort(preds)[::-1][:3]
    ]
    return label, confidence, top3
