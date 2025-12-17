import requests
from bs4 import BeautifulSoup
import time

# Reuse one session for speed (connection pooling)
_session = requests.Session()
_headers = {"User-Agent": "Tufts-DH-Scraper/1.0 (educational; contact: joseph.marmo@tufts.edu)"}

# How polite/fast you want to be
REQUEST_DELAY_SECONDS = 0.1  # was 1.0

def getsoup(url):
    s = _session.get(url, headers=_headers, timeout=25)
    s.raise_for_status()
    soup = BeautifulSoup(s.content, "html.parser")
    return soup

def getcontents(body):
    paragraphs = []
    for paragraph in body.find_all("p"):
        text = paragraph.text.strip()
        if text != "":
            paragraphs.append(text)
    return "\n\n".join(paragraphs) if paragraphs else ""

def getlinks(body):
    links = []
    for a in body.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/wiki/") and ":" not in href:
            links.append("https://en.wikipedia.org" + href)
    return links

def getlinknodes(links, depth, max_depth, num_nodes):
    if depth >= max_depth:
        return []

    link_nodes = []

    # IMPORTANT: this makes "8 nodes per page" actually return 8
    for link in links[:num_nodes]:
        time.sleep(REQUEST_DELAY_SECONDS)

        soup2 = getsoup(link)
        body2 = soup2.find("div", {"id": "mw-content-text"})
        if body2 is None:
            continue

        link_title = soup2.find("h1", id="firstHeading").text
        link_contents = getcontents(body2)
        links_link = getlinks(body2)

        link_links_nodes = getlinknodes(links_link, depth + 1, max_depth, num_nodes)

        link_nodes.append({
            "title": link_title,
            "content": link_contents,
            "url": link,
            "links": link_links_nodes
        })

    return link_nodes

def scrape(url, num_nodes, max_depth):
    soup = getsoup(url)
    body = soup.find("div", {"id": "mw-content-text"})
    if body is None:
        raise ValueError("Could not find main content div on this page.")

    title = soup.find("h1", id="firstHeading").text
    contents = getcontents(body)
    links = getlinks(body)
    link_nodes = getlinknodes(links, 0, max_depth, num_nodes)

    return {
        "title": title,
        "content": contents,
        "url": url,
        "links": link_nodes
    }
