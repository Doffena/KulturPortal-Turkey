import os, datasets, evaluate
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer

MODEL = "dbmdz/bert-base-turkish-cased"
DATA = "data/processed/monuments.jsonl"
OUT  = "runs/cls"

def load_dataset(path):
    return datasets.load_dataset("json", data_files={"train": path, "validation": path})

def main():
    ds = load_dataset(DATA)

    # Demo label: city (replace with your target label)
    labels = sorted(set([x["city"] for x in ds["train"] if x.get("city")]))
    label2id = {l:i for i,l in enumerate(labels)}
    id2label = {i:l for l,i in label2id.items()}

    tok = AutoTokenizer.from_pretrained(MODEL)
    def tokenize(batch):
        return tok(batch.get("text_clean",""), truncation=True)
    ds = ds.map(tokenize, batched=True)
    ds = ds.filter(lambda x: x.get("city") in label2id)
    ds = ds.map(lambda x: {"labels": label2id[x["city"]]})

    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=len(labels), id2label=id2label, label2id=label2id)

    acc = evaluate.load("accuracy")
    f1m = evaluate.load("f1")
    def metrics(p):
        import numpy as np
        preds = p.predictions.argmax(-1)
        return {
            "accuracy": acc.compute(references=p.label_ids, predictions=preds)["accuracy"],
            "f1_macro": f1m.compute(references=p.label_ids, predictions=preds, average="macro")["f1"]
        }

    args = TrainingArguments(
        output_dir=OUT,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=3,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        report_to="none"
    )

    tr = Trainer(model=model, args=args, train_dataset=ds["train"], eval_dataset=ds["validation"], tokenizer=tok, compute_metrics=metrics)
    tr.train()
    tr.save_model(os.path.join(OUT, "best"))
    tok.save_pretrained(os.path.join(OUT, "best"))
    print("[✓] training finished -> runs/cls/best")

if __name__ == "__main__":
    main()
