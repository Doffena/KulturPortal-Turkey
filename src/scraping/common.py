import random, time, re
from contextlib import contextmanager

def polite_sleep(min_s=1.0, max_s=2.0):
    import random, time
    time.sleep(random.uniform(min_s, max_s))

def clean_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())

@contextmanager
def step(msg: str):
    print(f"[+] {msg} ...", flush=True)
    try:
        yield
        print(f"[✓] {msg}", flush=True)
    except Exception as e:
        print(f"[x] {msg} -> {e}", flush=True)
        raise
