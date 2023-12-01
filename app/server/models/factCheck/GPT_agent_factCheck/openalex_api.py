from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import time

def fetch_wikidata(wikidata_id):
    url = f'https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json'
    try:
        return requests.get(url).json()
    except:
        return 'There was and error'
def clean_str(p):
  return p.encode().decode("unicode-escape").encode("latin1").decode("utf-8")


def create_abstract(invtext):
    wordlist = {}
    for k in invtext:
        for p in invtext[k]:
            wordlist[p] = k
    textlength = len(wordlist.keys())

    words = [wordlist[i] if i in wordlist else ' ' for i in range(textlength)]
    return ' '.join(words)
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
    """
    :param url: url to a wikipedia page
    filters all text in the wiki page
    :return: text in the page
    """
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

def get_concepts(concept):
    """
    :param concept: a concept
    get information about the concept: wiki pages, define of concept and relation nodes of the concept
    :return: information about the concept
    """
    print("Crawl the evidence links from Open Alex")
    url = f'https://api.openalex.org/concepts?search={concept}'
    wiki_re = ''
    wikidata_json = ''
    r = requests.get(url.strip()).json()
    # print(r)
    results = r["results"]
    for re in results:
        if 'ids' in re:
            url_wikipedia = re['ids']['wikipedia']
            wiki_re = wiki_crawler(url_wikipedia)
            # print(wiki_re)
        if 'wikidata' in re:
            url_wikidata = re['wikidata']
            wikidata_id = url_wikidata.split("/")[-1]
            wikidata_json = fetch_wikidata(wikidata_id)
    # import pdb
    # pdb.set_trace()
    return wiki_re, wikidata_json

def get_works_concepts(concept : str):
    """
    :param concept: a concept
    :return: dictionary with id of paper and abstract of this paper
    [
        {
            'id': ''
            'abstract': ''
        }
    ]
    """
    print("Crawl the evidence links from Open Alex")
    url = f'https://api.openalex.org/works?search={concept}'
    r = requests.get(url.strip()).json()
    results = r['results']
    abstract_list = []
    for re in results:
        id = re['id']
        title = re['title']
        open_access = re['open_access']
        abstract_inverted_index = re['abstract_inverted_index']
        # print(abstract_inverted_index)
        if abstract_inverted_index is not None:
            abstract = create_abstract(abstract_inverted_index)
            abstract_dict = {}
            abstract_dict['id'] = id
            abstract_dict['title'] = title
            abstract_dict['abstract'] = abstract
            abstract_list.append(abstract_dict)
    return abstract_list

if __name__ == "__main__":
    # wiki_re, wikidata_json = get_concepts("Creatine")
    # print(wiki_re)
    # print(wikidata_json)
    abstract_dict = get_works_concepts("Creatine")
    print(abstract_dict)
    pass