"""
inference.py
============
Real inference logic for:
   CNN-only path   my_model.keras        (image only)
   Fusion path     fusion_classifier.pth (image + text via InceptionV3 + BERT)

All heavy ML imports are done LAZILY (inside loader functions) so that a
missing or broken package does not prevent the module itself from importing,
and app.py will not fall back to the dummy stubs.
"""

import os
import json
import traceback

# NOTE: KERAS_BACKEND is set lazily inside _load_cnn() / _load_inception()
# to avoid corrupting NumPy before PyTorch (used by sentence-transformers) loads.

# 
# Paths
# 
BASE_DIR           = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNN_MODEL_PATH     = os.path.join(BASE_DIR, "CNN_models",  "my_model.keras")
FUSION_MODEL_PATH  = os.path.join(BASE_DIR, "Bert_Models", "fusion_classifier.pth")
DIAGNOSIS_MAP_PATH = os.path.join(BASE_DIR, "Bert_Models", "diagnosis_map.json")

# 
# Constants  (must match training config)
# 
IMAGE_SIZE   = (256, 256)        # CNN model input resolution (detected from model)
MAX_TEXT_LEN = 50
BERT_MODEL   = "bert-base-uncased"
IMG_FEAT_DIM = 2048              # InceptionV3 GlobalAveragePooling output
HIDDEN_DIM   = 512
DROPOUT      = 0.3

# 
# Diagnosis map
# 
try:
    with open(DIAGNOSIS_MAP_PATH, "r") as f:
        _raw_map = json.load(f)
    DIAGNOSIS_MAP = {int(k): v for k, v in _raw_map.items()}
except Exception:
    DIAGNOSIS_MAP = {0: "Glaucoma", 1: "Cataract", 2: "Retinal Disease", 3: "Normal"}

num_classes = len(DIAGNOSIS_MAP)

# 
# Lazy model cache
# 
_cnn_model       = None   # Keras CNN
_inception_model = None   # InceptionV3 feature extractor
_fusion_model    = None   # PyTorch FusionClassifier
_tokenizer       = None   # BERT tokenizer


# 
# FusionClassifier  (must mirror training code)
# 
def _build_fusion_classifier(torch, nn, num_classes):
    from transformers import BertModel

    class FusionClassifier(nn.Module):
        def __init__(self, num_classes=4, hidden_dim=512, dropout=0.3):
            super().__init__()
            self.text_encoder = BertModel.from_pretrained('bert-base-uncased')
            self.img_proj = nn.Sequential(
                nn.Linear(2048, 768),
                nn.ReLU(),
                nn.LayerNorm(768)
            )
            self.classifier = nn.Sequential(
                nn.Linear(768 * 2, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim // 2, num_classes)
            )

        def forward(self, image, input_ids, attention_mask):
            text_out = self.text_encoder(
                input_ids=input_ids,
                attention_mask=attention_mask
            ).pooler_output                            # (B, 768)
            img_out = self.img_proj(image)             # (B, 768)
            fused = torch.cat([text_out, img_out], dim=1)  # (B, 1536)
            return self.classifier(fused)              # (B, 4)

    return FusionClassifier


# 
# Loader helpers  (lazy, load once)
# 
def _load_cnn():
    global _cnn_model
    if _cnn_model is None:
        # Set backend here, right before TF is imported for the first time
        os.environ.setdefault("KERAS_BACKEND", "tensorflow")
        from tensorflow import keras
        print(f"[inference] Loading CNN model from {CNN_MODEL_PATH} ")
        _cnn_model = keras.models.load_model(CNN_MODEL_PATH)
        print("[inference]  CNN model loaded.")
    return _cnn_model


def _load_inception():
    global _inception_model
    if _inception_model is None:
        # Set backend here, right before TF is imported for the first time
        os.environ.setdefault("KERAS_BACKEND", "tensorflow")
        from tensorflow import keras
        from tensorflow.keras.applications import InceptionV3
        from tensorflow.keras.layers import GlobalAveragePooling2D
        print("[inference] Building InceptionV3 feature extractor ")
        base = InceptionV3(weights="imagenet", include_top=False,
                           input_shape=(299, 299, 3))
        _inception_model = keras.Model(
            inputs=base.input,
            outputs=GlobalAveragePooling2D()(base.output)
        )
        print("[inference]  InceptionV3 feature extractor ready.")
    return _inception_model


def _load_fusion():
    global _fusion_model, _tokenizer
    if _fusion_model is None:
        import torch
        import torch.nn as nn
        from transformers import BertTokenizer
        print(f"[inference] Loading FusionClassifier from {FUSION_MODEL_PATH} ")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _tokenizer    = BertTokenizer.from_pretrained(BERT_MODEL)
        FusionClassifier = _build_fusion_classifier(torch, nn, num_classes)
        _fusion_model    = FusionClassifier().to(device)
        state = torch.load(FUSION_MODEL_PATH, map_location=device)
        _fusion_model.load_state_dict(state)
        _fusion_model.eval()
        print("[inference]  FusionClassifier loaded.")
    return _fusion_model, _tokenizer


# 
# Feature Extraction
# 
def _extract_inception_feature(img_path: str):
    from PIL import Image
    import numpy as np
    from tensorflow.keras.applications.inception_v3 import preprocess_input
    
    inception_extractor = _load_inception()
    
    img = Image.open(img_path).convert('RGB')
    img = img.resize((299, 299))
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)           # (1, 299, 299, 3)
    arr = preprocess_input(arr)                 # scale to [-1, 1]
    feat = inception_extractor.predict(arr, verbose=0)[0]  # (2048,)
    return feat


# 
# Public API
# 
# ── EXACT PREPROCESSING PIPELINE ──────────────────────────────────────────────
def preprocess_image(image_file):
    from PIL import Image
    import numpy as np
    
    img = Image.open(image_file).convert('RGB')
    img = img.resize((256, 256))
    img_array = np.array(img, dtype=np.float32)          # shape: (256, 256, 3)
    img_array = np.expand_dims(img_array, axis=0)        # shape: (1, 256, 256, 3)
    img_array = img_array / 255.0                        # scale to [0, 1]
    return img_array

# ── EXACT PREDICTION PIPELINE ────────────────────────────────────────────────
def predict_cnn(image_path: str) -> dict:
    """
    Run image-only inference using the Keras CNN model.
    Returns dict with keys: diagnosis (str), confidence (float 0-1), all_probs (dict)
    """
    try:
        import numpy as np

        CLASS_NAMES = ['Cataract', 'Diabetic Retinopathy', 'Glaucoma', 'Normal']
        model = _load_cnn()

        # 1. Preprocess using exact pipeline
        img_array = preprocess_image(image_path)

        # 2. Predict
        preds = model.predict(img_array, verbose=0)
        predicted_index = int(np.argmax(preds[0]))
        predicted_class = CLASS_NAMES[predicted_index]
        confidence = float(preds[0][predicted_index])
        all_probs = {CLASS_NAMES[i]: float(preds[0][i]) for i in range(4)}

        return {
            "diagnosis": predicted_class,
            "confidence": confidence,
            "all_probs": all_probs,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        err_msg = str(e)
        if len(err_msg) > 200:
            err_msg = err_msg[:200] + "..."
        return {"diagnosis": f"CNN Error: {err_msg}", "confidence": 0.0}


def predict_fusion(image_path: str, caption: str) -> dict:
    """
    Run multi-modal inference (InceptionV3 image + BERT text).
    Returns dict with keys: diagnosis (str), confidence (float), all_probs (dict)
    """
    try:
        import numpy as np
        import torch
        import torch.nn.functional as F

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model, tokenizer = _load_fusion()

        # Image feature
        img_feat   = _extract_inception_feature(image_path)
        img_tensor = torch.tensor(img_feat, dtype=torch.float32).unsqueeze(0).to(device)

        # Tokenise caption
        tokens = tokenizer(
            caption,
            padding="max_length",
            truncation=True,
            max_length=MAX_TEXT_LEN,
            return_tensors="pt"
        )
        ids   = tokens["input_ids"].to(device)
        masks = tokens["attention_mask"].to(device)

        # Inference
        with torch.no_grad():
            logits = model(img_tensor, ids, masks)
            probs  = F.softmax(logits, dim=1)[0].cpu().numpy()

        pred_idx   = int(probs.argmax())
        confidence = float(probs.max())
        diagnosis  = DIAGNOSIS_MAP.get(pred_idx, f"Class {pred_idx}")
        all_probs  = {DIAGNOSIS_MAP.get(i, str(i)): float(probs[i])
                      for i in range(num_classes)}

        return {"diagnosis": diagnosis, "confidence": confidence, "all_probs": all_probs}

    except Exception as e:
        traceback.print_exc()
        err_msg = str(e)
        if len(err_msg) > 200:
            err_msg = err_msg[:200] + "..."
        return {"diagnosis": f"Fusion Error: {err_msg}", "confidence": 0.0}
