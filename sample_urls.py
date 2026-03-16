#!/usr/bin/env python3
"""
Sample test URLs from data_30k.csv (column: properties.ccm:wwwurl).
Strategy: max MAX_PER_DOMAIN per domain, shuffle, write to test_urls.txt.
Run once before loadtest.py.
"""

import csv
import random
from collections import Counter, defaultdict
from urllib.parse import urlparse

CSV_FILE       = "data_30k.csv"
OUTPUT_FILE    = "test_urls.txt"
TARGET_COUNT   = 80
MAX_PER_DOMAIN = 2
RANDOM_SEED    = 42

# Domains that produce no extractable text (video players, interactive tools, file stores)
SKIP_DOMAINS = {
    "www.youtube.com", "youtu.be", "youtube.com",
    "vimeo.com", "www.vimeo.com",
    "learningapps.org", "www.learningapps.org",
    "www.geogebra.org", "geogebra.org",
    "apps.zum.de",
    "media.sodis.de",
    "cloud.schulcampus-rlp.de",
    "moodle.org", "www.moodle.org",
    "padlet.com", "www.padlet.com",
    "oncoo.de", "www.oncoo.de",
    "h5p.org", "www.h5p.org",
    "kahoot.com", "www.kahoot.com",
}

# URL fragments that indicate direct file downloads (not web pages)
SKIP_EXTENSIONS = (".pdf", ".mp4", ".mp3", ".zip", ".docx", ".pptx", ".xlsx",
                   ".avi", ".mov", ".ogg", ".wav", ".png", ".jpg", ".jpeg", ".gif")


def load_urls() -> list:
    urls = []
    with open(CSV_FILE, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            val = row.get("properties.ccm:wwwurl", "").strip()
            if not val.startswith("http"):
                continue
            path = urlparse(val).path.lower()
            if any(path.endswith(ext) for ext in SKIP_EXTENSIONS):
                continue
            urls.append(val)
    return urls


def sample_diverse(urls: list, max_per_domain: int, target: int) -> list:
    random.seed(RANDOM_SEED)
    random.shuffle(urls)

    per_domain: dict = defaultdict(list)
    for url in urls:
        domain = urlparse(url).netloc
        if domain in SKIP_DOMAINS:
            continue
        if len(per_domain[domain]) < max_per_domain:
            per_domain[domain].append(url)

    flat = [url for bucket in per_domain.values() for url in bucket]
    random.shuffle(flat)
    return flat[:target]


def main() -> None:
    urls = load_urls()
    unique = list(dict.fromkeys(urls))          # preserve order, deduplicate
    print(f"Loaded {len(urls)} URLs  ({len(unique)} unique, after filtering files/videos)")

    sampled = sample_diverse(unique, MAX_PER_DOMAIN, TARGET_COUNT)
    domains = Counter(urlparse(u).netloc for u in sampled)

    print(f"Sampled {len(sampled)} URLs across {len(domains)} domains\n")
    print("Domain distribution:")
    for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {count}x  {domain}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for url in sampled:
            f.write(url + "\n")
    print(f"\nSaved → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
