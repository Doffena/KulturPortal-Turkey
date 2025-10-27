import sys, requests, yaml
from urllib.parse import urljoin

def main(cfg_path="configs/scraping.yaml"):
    cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))
    robots = urljoin(cfg["base_url"], "/robots.txt")
    r = requests.get(robots, timeout=10, headers={"User-Agent": cfg["user_agent"]})
    print(f"[robots] {robots} -> {r.status_code}")
    print(r.text[:1500])

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "configs/scraping.yaml")
