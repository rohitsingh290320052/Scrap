import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def extract_meta(soup):
    desc = None
    keywords = None
    d = soup.find("meta", attrs={"name":"description"})
    if d and d.get("content"):
        desc = d["content"].strip()
    k = soup.find("meta", attrs={"name":"keywords"})
    if k and k.get("content"):
        keywords = k["content"].strip()
    # also og:description
    og = soup.find("meta", attrs={"property":"og:description"})
    if og and og.get("content") and not desc:
        desc = og["content"].strip()
    return desc, keywords

def scrape_site(url, limit_images=10, snippet_length=1000):
    url = normalize_url(url)
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        resp.raise_for_status()
    except Exception as e:
        return {"error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")

    # Title
    title = soup.title.string.strip() if soup.title and soup.title.string else url

    # Meta
    meta_desc, meta_keywords = extract_meta(soup)

    # Images (resolve to absolute)
    imgs = []
    for img in soup.find_all("img", src=True):
        src = img.get("src").strip()
        abs_src = urljoin(url, src)
        imgs.append(abs_src)
        if len(imgs) >= limit_images:
            break

    first_image = imgs[0] if imgs else None

    # Headings (h1..h3 preferred)
    headings = []
    for level in ("h1","h2","h3","h4"):
        for h in soup.find_all(level):
            text = h.get_text(strip=True)
            if text:
                headings.append({"tag": level, "text": text})
    # Links count and domain
    links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href").strip()
        abs_href = urljoin(url, href)
        links.append(abs_href)
    links_count = len(links)

    domain = urlparse(url).netloc

    # small HTML/text snippet for modal preview (first N chars of body)
    body = soup.body.get_text(separator=" ", strip=True) if soup.body else soup.get_text(separator=" ", strip=True)
    content_snippet = body[:snippet_length] + ("..." if len(body) > snippet_length else "")

    return {
        "title": title,
        "url": url,
        "meta_description": meta_desc,
        "meta_keywords": meta_keywords,
        "first_image": first_image,
        "images": json.dumps(imgs, ensure_ascii=False),
        "headings": json.dumps(headings, ensure_ascii=False),
        "links_count": links_count,
        "domain": domain,
        "content_snippet": content_snippet
    }
