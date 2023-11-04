from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import time



def clean_str(p):
  return p.encode().decode("unicode-escape").encode("latin1").decode("utf-8")

def get_page_obs(page):
    # find all paragraphs
    paragraphs = page.split("\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # find all sentence
    sentences = []
    for p in paragraphs:
        sentences += p.split('. ')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    return ' '.join(sentences[:5])
def wiki_crawler(url):
    response_text = requests.get(url).text
    soup = BeautifulSoup(response_text, features="html.parser")
    result_divs = soup.find_all("div", {"class": "mw-search-result-heading"})
    if result_divs:  # mismatch
        result_titles = [clean_str(div.get_text().strip()) for div in result_divs]
        obs = f"Could not find {url} in {result_titles}"
    else:
        page = [p.get_text().strip() for p in soup.find_all("p") + soup.find_all("ul")]
        page_z = ""
        for p in page:
            if len(p.split(" ")) > 2:
                page_z += clean_str(p)
                if not p.endswith("\n"):
                    page_z += "\n"
        obs = get_page_obs(page_z)
    return obs

def get_concepts(drug):
    print("Crawl the evidence links from Google Search")
    url = f'https://api.openalex.org/concepts?search={drug}'
    wiki_re = ''
    r = requests.get(url.strip()).json()
    # print(r)
    results = r["results"]
    for re in results:
        if 'ids' in re:
            url_wikipedia = re['ids']['wikipedia']
            wiki_re = wiki_crawler(url_wikipedia)
            print(wiki_re)
    # import pdb
    # pdb.set_trace()
    return wiki_re


if __name__ == "__main__":
    links = get_concepts("Creatine")

    pass