from fastapi import FastAPI, Query
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = FastAPI(title="Kultur Portal Monuments API")

CKPT = "runs/cls/best"
tok = AutoTokenizer.from_pretrained(CKPT)
mdl = AutoModelForSequenceClassification.from_pretrained(CKPT)
mdl.eval()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/classify")
def classify(text: str = Query(..., description="Monument description (clean text)")):
    x = tok(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = mdl(**x).logits
        pred_id = int(logits.argmax(-1))
        score = float(logits.softmax(-1).max())
    label = mdl.config.id2label.get(pred_id, str(pred_id))
    return {"label": label, "score": score}
