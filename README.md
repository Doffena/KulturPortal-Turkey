# Kultur Portal Monuments — Dataset & Fine‑Tuned Model (TR/EN)

This repository collects **public monument data** from Turkey’s official **Cultural Portal**, builds a **structured dataset**, and fine‑tunes a Turkish NLP model for QA/retrieval/classification with a target of **≥80% validation accuracy** on the chosen task. Scraping follows `robots.txt` and ToS. A FastAPI endpoint provides inference.

>  Only public pages are scraped. Respect robots.txt and terms. Keep **source URLs** in the dataset and credit the source.

---

## 🇹🇷 Türkçe Açıklama

### Amaç
- Kültür Portalı’ndan **kamusal anıt sayfalarını** gezip **yapılandırılmış veri kümesi** oluşturmak
- Bu veriyle bir **Türkçe NLP modelini fine‑tune** etmek (sınıflandırma, QA veya retrieval)
- **≥%80 doğruluk** hedefi (göreve uygun metrik: Accuracy / F1 / EM-F1)
- **FastAPI** ile sorgulanabilir bir uç nokta

### Hızlı Başlangıç
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
pip install -r requirements.txt

# 1) robots.txt görüntüle
python -m src.scraping.robots_check

# 2) listing sayfalarını çek
python -m src.scraping.fetch_listing --config configs/scraping.yaml

# 3) detay sayfalarını çek
python -m src.scraping.fetch_detail --config configs/scraping.yaml

# 4) ön‑işleme
python -m src.preprocess.clean_normalize --config configs/scraping.yaml

# 5) (opsiyonel) eğitim + değerlendirme
python -m src.modeling.train --task classify
python -m src.modeling.evaluate --task classify

# 6) API
uvicorn src.app.api:app --host 0.0.0.0 --port 8000
```

### Dizin Yapısı
```
kultur-portal-monuments/
├─ configs/scraping.yaml
├─ data/
│  ├─ raw/          # listing.jsonl, detail.jsonl
│  └─ processed/    # monuments.jsonl
├─ src/
│  ├─ scraping/     # robots_check, fetch_listing, fetch_detail
│  ├─ preprocess/   # clean_normalize
│  ├─ modeling/     # train, evaluate
│  └─ app/          # FastAPI
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## 🇬🇧 English Summary

**Goal**: Crawl **public pages** from the Cultural Portal, build a **structured dataset**, **fine‑tune** a Turkish model, and serve **API** inference. Targets **≥80% validation accuracy** (task‑specific metric).

### Notes
- Update CSS selectors in `configs/scraping.yaml` to match the portal’s DOM if needed.
- Keep crawl rate polite (1–2s). Increase if you get throttled.
- Use separate train/validation splits before training for real experiments.

Bu proje **Burak AVCI** tarafından geliştirilmiştir.  
 burakavci0206@gmail.com
