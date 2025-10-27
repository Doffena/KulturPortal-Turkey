import os, json, yaml, argparse, re

def clean_text(t: str) -> str:
    t = (t or "").replace("\u200b", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t

def main(cfg_path="configs/scraping.yaml"):
    cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))
    inp = cfg["storage"]["detail_jsonl"]
    outp = cfg["storage"]["processed_jsonl"]
    os.makedirs(os.path.dirname(outp), exist_ok=True)

    with open(inp, "r", encoding="utf-8") as fin, open(outp, "w", encoding="utf-8") as fout:
        for line in fin:
            x = json.loads(line)
            x["text_clean"] = clean_text(x.get("description",""))
            fout.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"[✓] wrote {outp}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/scraping.yaml")
    args = ap.parse_args()
    main(args.config)
