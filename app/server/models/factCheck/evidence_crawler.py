# !pip install newspaper3k
from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import time

def parse_passages(url):
    
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    config = Config()
    config.browser_user_agent = user_agent
    config.request_timeout = 10
    
    try: 
        article = Article(url, config=config)
        article.download()
        article.parse()
    
    except Exception as e:
        print(url, e)
        return None
    
    raw_passages = article.text.split("\n\n")        
    ret_passages = []
    cache = ""
    
    for text in raw_passages:
        text = text.strip()
        if len(text.split(" ")) <= 6:    #High chance to be a title, append to the next passage        
            cache += text
        else: 
            if len(cache) > 0:
                ret_passages.append(cache + ". " + text)
                cache = ""
            else:                
                ret_passages.append(text)
        
    return ret_passages, url 

def get_evidence_links(claim):    
    HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    links = []
    claim = claim.strip().replace(" ","+")
#     for i in [0, 10, 20]:
    for i in [0]:
        url  = "https://www.google.com/search?q={claim}&start={i}"
        r = requests.get(url.strip(), headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        search_result = soup.find("div", attrs={"id": "search"})
        for div in search_result.findAll('a'):
            if 'data-ved' in div.attrs and 'ping' in div.attrs:
                links.append(div['href'])
#         time.sleep(5)

    return links

def crawl_evidences(claim):
    print("Crawl the evidence links from Google Search")
    start = time.perf_counter()
    links = get_evidence_links(claim)    
    end = time.perf_counter()
    print("It took {:.2f} second(s) to finish.".format(end-start))

    print("Crawl the evidences")
    start = time.perf_counter()
    with ThreadPoolExecutor() as executor:
        results = executor.map(parse_passages, links)
    end = time.perf_counter()

    print("It took {:.2f} second(s) to finish.".format(end-start))

    candidates = []
    candidate_url_dict = {}
    for result in results:
        if result is not None:
            evis, url = result
            if len(evis) > 0:
                candidates.extend(evis)
                for e in evis:
                    candidate_url_dict[e] = url
                
    return candidates, candidate_url_dict





