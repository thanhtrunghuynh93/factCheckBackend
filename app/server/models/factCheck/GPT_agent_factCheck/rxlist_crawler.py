# !pip install newspaper3k
from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import time


def parse_passages(url):
    response_text = requests.get(url).text
    soup = BeautifulSoup(response_text, features="html.parser")
    # result_div = soup.find_all("div", {"class": "w-full"})[0]
    text_list = [p.get_text().strip() for p in soup.find_all("p") + soup.find_all("li")][1:]
    text = " ".join(text_list)
    # print(text)
    return text


def get_evidence_links(drug):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    links_drug = []
    links_dict = []
    links_other = []
    # claim = claim.strip().replace(" ", "%20")
    #     for i in [0, 10, 20]:
    url = f'https://www.rxlist.com/search/rxl/{drug}'
    r = requests.get(url.strip(), headers=HEADERS)
    print(r.status_code)
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup)
    search_result = soup.find("div", attrs={"class": "searchresults main"})
    if search_result is None:
        print("Error in crawling google links".format(soup.text))
        return [], [], []
    divs = search_result.findAll('a')
    for div in divs:
        links_drug.append(div['href'])

    search_result = soup.find("div", attrs={"class": "searchresults dict"})
    if search_result is not None:
        divs = search_result.findAll('a')
        for div in divs:
            links_dict.append(div['href'])

    search_result = soup.find("div", attrs={"class": "searchresults other"})
    if search_result is not None:
        divs = search_result.findAll('a')
        for div in divs:
            links_other.append(div['href'])

    return links_drug, links_dict, links_other


def crawl_evidences(drug):
    print("Crawl the evidence links from Google Search")
    start = time.perf_counter()
    links_drug, links_dict, links_other = get_evidence_links(drug)
    end = time.perf_counter()
    print("It took {:.2f} second(s) to finish.".format(end - start))

    print("Crawl the evidences")
    start = time.perf_counter()
    with ThreadPoolExecutor() as executor:
        results = executor.map(parse_passages, [links_drug[0], links_dict[0], links_other[0]])
        # results = executor.map(parse_passages, [links_drug[0]])
    end = time.perf_counter()

    print("It took {:.2f} second(s) to finish.".format(end - start))

    candidates = []
    candidate_url_dict = {}
    text_all = ""
    for result in results:
        if result is not None:
            text_all += result

    return text_all

if __name__ == "__main__":
    links = get_evidence_links("Creatine")
    text_all = crawl_evidences("Creatine")
    # print(links)
    print(text_all)
    # print(candidate_url_dict)


    pass