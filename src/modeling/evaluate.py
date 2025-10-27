import datasets, evaluate
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

CKPT = "runs/cls/best"
DATA = "data/processed/monuments.jsonl"

def main():
    tok = AutoTokenizer.from_pretrained(CKPT)
    mdl = AutoModelForSequenceClassification.from_pretrained(CKPT)

    ds = datasets.load_dataset("json", data_files={"validation": DATA})["validation"]
    inv = {v:k for k,v in mdl.config.id2label.items()}
    ds = ds.filter(lambda x: x.get("city") in inv)

    acc = evaluate.load("accuracy")
    f1m = evaluate.load("f1")

    preds, refs = [], []
    for ex in ds:
        x = tok(ex.get("text_clean",""), return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = mdl(**x).logits
        preds.append(int(logits.argmax(-1)))
        refs.append(int(inv[ex["city"]]))

    print("accuracy:", acc.compute(references=refs, predictions=preds))
    print("f1_macro:", f1m.compute(references=refs, predictions=preds, average="macro"))

if __name__ == "__main__":
    main()
