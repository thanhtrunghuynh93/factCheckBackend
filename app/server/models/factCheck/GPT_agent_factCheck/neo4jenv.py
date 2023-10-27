import ast
import json
import time
import gym
import requests
from bs4 import BeautifulSoup
from neomodel import StructuredNode, StringProperty, RelationshipTo, RelationshipFrom, config
from neomodel import config
class Drug_ID(StructuredNode):
    compound_id = StringProperty(unique_index=True)
    name = StringProperty()
    effect = RelationshipTo('Side_Effect', 'effect')

class Side_Effect(StructuredNode):
    umls_id = StringProperty(unique_index=True)
    name = StringProperty()
    drug = RelationshipFrom('Drug_ID', 'effect')

# import wikipedia
config.DATABASE_URL = 'bolt://neo4j:12345678@100.64.241.89:7687'


class textSpace(gym.spaces.Space):
    def contains(self, x) -> bool:
        """Return boolean specifying if x is a valid member of this space."""
        return isinstance(x, str)


class Neo4jEnv(gym.Env):

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
        self.effects = []

    def _get_obs(self):
        return self.obs

    def _get_info(self):
        return {"steps": self.steps, "answer": self.answer}

    def reset(self, seed=None, return_info=False, options=None):
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
        self.drug = None
        self.effects = []
        observation = self._get_obs()
        info = self._get_info()
        return (observation, info) if return_info else observation

    def search_step(self, drug_name):
        self.drug = Drug_ID.nodes.get_or_none(name=drug_name)
        relation = self.drug.effect
        for i in relation:
            # print(i)
            self.effects.append(i.name.lower())

    def step(self, action):
        reward = 0
        done = False
        action = action.strip()
        if self.answer is not None:  # already finished
            done = True
            return self.obs, reward, done, self._get_info()

        if action.startswith("search[") and action.endswith("]"):
            drug_name = action[len("search["):-1]
            self.search_step(drug_name)
            self.obs = drug_name + " have some effects : " + ",".join(i for i in self.effects)
            print(self.obs)
        elif action.startswith("lookup[") and action.endswith("]"):
            keyword = action[len("lookup["):-1]
            if keyword.lower() in self.effects:  # reset lookup
                self.obs = "This drug have effect " + keyword
            else:
                self.obs = "This drug do not have effect " + keyword

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
