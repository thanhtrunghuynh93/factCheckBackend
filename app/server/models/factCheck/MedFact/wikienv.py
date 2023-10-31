import time
import gym
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from sentence_transformers import SentenceTransformer
from server.models.factCheck.evidence_filter import get_diversed_evidences, print_evidences
from server.models.factCheck.GPT_factCheck import get_completion
from server.models.factCheck.MedFact.rxlist_crawler import crawl_evidences


# import wikipedia

def is_drug(input):
  prompt = 'Is {} a name of any drug, chemical compound or vaccine? Answer only "Yes" or "No".'.format(input)
  answer = get_completion(prompt)
  if "Yes" in answer:
    return True
  return False

def clean_str(p):
  return p.encode().decode("unicode-escape").encode("latin1").decode("utf-8")

def clean_brackets(input):
    res = []
    es = input.split("[")
    for e in es:
        res.append(e.split("]")[-1])
    return " ".join(res)

def parse_passages(html):
    article = Article(url = '')
    article.set_html(html)
    article.parse()

    raw_passages = article.text.split("\n\n")        
    ret_passages = []
    cache = ""
    
    for text in raw_passages:
        text = text.strip()
        if len(text.split(" ")) <= 10:    #High chance to be a title, append to the next passage     
            if cache == "":
                cache = text
            else:
                cache += ". {}".format(text)
        else: 
            if len(cache) > 0:
                ret_passages.append(cache + ". " + text)
                cache = ""
            else:                
                ret_passages.append(text)

    for i in range(len(ret_passages)):
        ret_passages[i] = clean_brackets(ret_passages[i])
        # ret_passages[i] = ". ".join([p.strip() for p in ret_passages[i].split(".")])
        
    return ret_passages

class textSpace(gym.spaces.Space):
  def contains(self, x) -> bool:
    """Return boolean specifying if x is a valid member of this space."""
    return isinstance(x, str)


class WikiEnv(gym.Env):

  def __init__(self):
    """
      Initialize the environment.
    """
    super().__init__()
    self.page = None  # current Wikipedia page
    self.obs = None  # current observation
    self.lookup_keyword = None  # current lookup keyword
    self.lookup_list = None  # list of paragraphs containing current lookup keyword
    self.lookup_cnt = None  # current lookup index
    self.steps = 0  # current number of steps
    self.answer = None  # current answer from the agent
    self.observation_space = self.action_space = textSpace()
    self.search_time = 0
    self.num_searches = 0
    self.sbert = SentenceTransformer('sentence-transformers/sentence-t5-base')

  def _get_obs(self):
    return self.obs

  def _get_info(self):
    return {"steps": self.steps, "answer": self.answer}

  def reset(self, claim, seed=None, return_info=False, options=None):
    # We need the following line to seed self.np_random
    # super().reset(seed=seed)
    self.obs = ("Interact with Wikipedia using search[], lookup[], and "
                "finish[].\n")
    self.page = None
    self.lookup_keyword = None
    self.lookup_list = None
    self.lookup_cnt = None
    self.steps = 0
    self.answer = None
    self.claim = claim
    observation = self._get_obs()
    info = self._get_info()
    return (observation, info) if return_info else observation

  def construct_lookup_list(self, keyword):
    # find all paragraphs
    if self.page is None:
      return []
    paragraphs = self.page.split("\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # find all sentence
    sentences = []
    for p in paragraphs:
      sentences += p.split('. ')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]

    parts = sentences
    parts = [p for p in parts if keyword.lower() in p.lower()]
    return parts

  @staticmethod
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

    # ps = page.split("\n")
    # ret = ps[0]
    # for i in range(1, len(ps)):
    #   if len((ret + ps[i]).split(" ")) <= 50:
    #     ret += ps[i]
    #   else:
    #     break
    # return ret

  def search_wiki(self, entity):
    entity_ = entity.replace(" ", "+")
    search_url = f"https://en.wikipedia.org/w/index.php?search={entity_}"
    old_time = time.time()
    response_text = requests.get(search_url).text
    self.search_time += time.time() - old_time
    self.num_searches += 1
    soup = BeautifulSoup(response_text, features="html.parser")
    result_divs = soup.find_all("div", {"class": "mw-search-result-heading"})
    if result_divs:  # mismatch
      self.result_titles = [clean_str(div.get_text().strip()) for div in result_divs]
      self.obs = f"Could not find {entity}. Similar: {self.result_titles[:5]}."
    else:
      page = [p.get_text().strip() for p in soup.find_all("p") + soup.find_all("ul")]
      if any("may refer to:" in p for p in page):
        self.search_step("[" + entity + "]")
      else:
        passages = parse_passages(response_text)
        evidences = get_diversed_evidences(self.sbert, self.claim, passages, beta=0.7, k=3)

        self.obs = ""
        for i in range(len(evidences)):
          e = evidences[i]
          self.obs += f"\nEvidence {i+1}: {e}\nSource: {search_url}"

        
        #  = self.get_page_obs("Evidence:".join(evidences))
        
        # self.page = ""
        # for p in page:
        #   if len(p.split(" ")) > 2:
        #     self.page += clean_str(p)
        #     if not p.endswith("\n"):
        #       self.page += "\n"
        # self.obs = self.get_page_obs(self.page)
        self.lookup_keyword = self.lookup_list = self.lookup_cnt = None

  def search_rxlist(self, entity):
    passages, url = crawl_evidences(entity)
    if passages is not None:
      evidences = get_diversed_evidences(self.sbert, self.claim, passages, beta=0.7, k=3)
      for i in range(len(evidences)):
        e = evidences[i]
        self.obs += f"\nEvidence {i+4}: {e}\nSource: {url}"
  
  def step(self, action):
    reward = 0
    done = False
    action = action.strip()
    if self.answer is not None:  # already finished
      done = True
      return self.obs, reward, done, self._get_info()
    
    if action.startswith("search[") and action.endswith("]"):
      entity = action[len("search["):-1]
      # entity_ = entity.replace(" ", "_")
      # search_url = f"https://en.wikipedia.org/wiki/{entity_}"
      self.search_wiki(entity)
      #Check if the entity is a compound/vaccine/drug, search for more info, if yes
      #Look for additional info (MedDRA, https://www.rxlist.com/)
      if is_drug(entity):
        self.search_rxlist(entity)
      
    elif action.startswith("lookup[") and action.endswith("]"):
      keyword = action[len("lookup["):-1]
      if self.lookup_keyword != keyword:  # reset lookup
        self.lookup_keyword = keyword
        self.lookup_list = self.construct_lookup_list(keyword)
        self.lookup_cnt = 0
      if self.lookup_cnt >= len(self.lookup_list):
        self.obs = "No more results.\n"
      else:
        self.obs = f"(Result {self.lookup_cnt + 1} / {len(self.lookup_list)}) " + self.lookup_list[self.lookup_cnt]
        self.lookup_cnt += 1
    elif action.startswith("finish[") and action.endswith("]"):
      answer = action[len("finish["):-1]
      self.answer = answer
      done = True
      self.obs = f"Episode finished, reward = {reward}\n"
    elif action.startswith("think[") and action.endswith("]"):
      self.obs = "Nice thought."
    else:
      self.obs = "Invalid action: {}".format(action)

    self.steps += 1

    return self.obs, reward, done, self._get_info()
  
  def get_time_info(self):
    speed = self.search_time / self.num_searches if self.num_searches else 0
    return {
        "call_speed": speed,
        "call_time": self.search_time,
        "num_calls": self.num_searches,
    }
