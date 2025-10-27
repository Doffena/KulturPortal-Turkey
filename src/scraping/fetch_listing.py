import os, json, requests, yaml
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import trange
from .common import polite_sleep, step, clean_ws

def fetch_listing(cfg):
    base = cfg["base_url"]
    path_tpl = cfg["paths"]["listing"]
    out_path = cfg["storage"]["listing_jsonl"]
    headers = {"User-Agent": cfg["user_agent"]}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with step(f"write listing -> {out_path}"):
        with open(out_path, "w", encoding="utf-8") as fout:
            for page in trange(1, cfg["max_pages"]+1, desc="listing"):
                url = urljoin(base, path_tpl.format(page=page))
                r = requests.get(url, timeout=cfg["timeout_seconds"], headers=headers)
                if r.status_code != 200:
                    break
                soup = BeautifulSoup(r.text, "lxml")
                cards = soup.select(cfg["selectors"]["listing_card"])
                if not cards:
                    break
                for a in cards:
                    href = a.get("href") or ""
                    title_el = a.select_one(cfg["selectors"].get("listing_title",""))
                    title = clean_ws(title_el.get_text()) if title_el else clean_ws(a.get_text())
                    if href:
                        item = {"title": title, "url": urljoin(base, href)}
                        fout.write(json.dumps(item, ensure_ascii=False) + "\n")
                polite_sleep(cfg["rate_seconds_min"], cfg["rate_seconds_max"])

def main(cfg_path="configs/scraping.yaml"):
    cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))
    fetch_listing(cfg)

if __name__ == "__main__":
    main()
