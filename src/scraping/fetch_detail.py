import os, json, yaml, requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime, timezone
from .common import polite_sleep, step, clean_ws

def parse_detail(soup, sel):
    title_el = soup.select_one(sel["detail_title"])
    content_el = soup.select_one(sel["detail_content"])
    city_el = soup.select_one(sel["detail_city"])
    district_el = soup.select_one(sel["detail_district"])

    return {
        "name": clean_ws(title_el.get_text()) if title_el else None,
        "description": clean_ws(content_el.get_text(" ")) if content_el else None,
        "city": clean_ws(city_el.get_text()) if city_el else None,
        "district": clean_ws(district_el.get_text()) if district_el else None,
    }

def fetch_detail(cfg):
    in_path = cfg["storage"]["listing_jsonl"]
    out_path = cfg["storage"]["detail_jsonl"]
    headers = {"User-Agent": cfg["user_agent"]}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with step(f"detail from {in_path} -> {out_path}"):
        with open(in_path, "r", encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
            for line in tqdm(fin, desc="detail"):
                item = json.loads(line)
                url = item["url"]
                r = requests.get(url, timeout=cfg["timeout_seconds"], headers=headers)
                if r.status_code != 200:
                    continue
                soup = BeautifulSoup(r.text, "lxml")
                data = parse_detail(soup, cfg["selectors"])
                data.update({
                    "source_url": url,
                    "last_crawled_at": datetime.now(timezone.utc).isoformat()
                })
                fout.write(json.dumps(data, ensure_ascii=False) + "\n")
                polite_sleep(cfg["rate_seconds_min"], cfg["rate_seconds_max"])

def main(cfg_path="configs/scraping.yaml"):
    cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))
    fetch_detail(cfg)

if __name__ == "__main__":
    main()
