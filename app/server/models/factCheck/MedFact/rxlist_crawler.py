# !pip install newspaper3k
from newspaper import Article, Config
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import time

# def parse_passages(url):
    
#     user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
#     config = Config()
#     config.browser_user_agent = user_agent
#     config.request_timeout = 10
    
#     try: 
#         article = Article(url, config=config)
#         article.download()
#         article.parse()
    
#     except Exception as e:
#         print(url, e)
#         return None
    
#     raw_passages = article.text.split("\n\n")        
#     ret_passages = []
#     cache = ""
    
#     for text in raw_passages:
#         text = text.strip()
#         if len(text.split(" ")) <= 10:    #High chance to be a title, append to the next passage        
#             cache += text
#         else: 
#             if len(cache) > 0:
#                 ret_passages.append(cache + ". " + text)
#                 cache = ""
#             else:                
#                 ret_passages.append(text)
        
#     return ret_passages

def parse_passages(url):
    response_text = requests.get(url).text
    soup = BeautifulSoup(response_text, features="html.parser")
    main = soup.find_all("div", {"class": "w-full"})
    
    if len(main) == 0:
        return None

    result_div = main[0]
    text_list = result_div.text.splitlines()
    text_list = [p for p in text_list if len(p) > 0]
    res = " ".join(text_list).split(".")
    res = [p.strip() for p in res]
    res = [p for p in res if len(p.split(" ")) > 1]

    # text_list = [p.get_text().strip() for p in soup.find_all("p") + soup.find_all("li")][1:]
    # text_list = [p for p in text_list if len(p) > 0]

    
    return res


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
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup)
    search_result = soup.find("div", attrs={"class": "searchresults main"})
    if search_result is None:
        print("Error in crawling rxlist links".format(soup.text))
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
    # print("Crawl the evidence links from RxList")
    # start = time.perf_counter()
    links_drug, links_dict, links_other = get_evidence_links(drug)

    # end = time.perf_counter()
    # print("It took {:.2f} second(s) to finish.".format(end - start))

    # print("Crawl the top 1 evidence")
    # start = time.perf_counter()

    res = parse_passages(links_drug[0])

    # end = time.perf_counter()

    return res, links_drug[0]

# def crawl_evidences(drug):
#     print("Crawl the evidence links from RxList")
#     start = time.perf_counter()
#     links_drug, links_dict, links_other = get_evidence_links(drug)
#     end = time.perf_counter()
#     print("It took {:.2f} second(s) to finish.".format(end - start))

#     print("Crawl the evidences")
#     start = time.perf_counter()
#     with ThreadPoolExecutor() as executor:
#         results = executor.map(parse_passages, [links_drug[0], links_dict[0], links_other[0]])
#         # results = executor.map(parse_passages, [links_drug[0]])
#     end = time.perf_counter()

#     print("It took {:.2f} second(s) to finish.".format(end - start))

#     candidates = []
#     candidate_url_dict = {}
#     text_all = ""
#     i = 0
#     for result in results:
#         if result is not None:
#             print(f"{i} \n\n")
#             text_all += result
#             i += 1 

#     return text_all

if __name__ == "__main__":
    links = get_evidence_links("Creatine")
    # print(links)
    res = crawl_evidences("Creatine")

    print(res)
    # # print(links)
    # print(text_all)
    # # print(candidate_url_dict)


    # pass