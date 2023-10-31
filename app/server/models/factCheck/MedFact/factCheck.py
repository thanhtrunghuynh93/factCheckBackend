from server.models.factCheck.MedFact.wikienv import WikiEnv
from server.models.factCheck.MedFact.wrappers import FactCheckWrapper

import os
import openai
import yaml
import requests
import json
 
# openai.api_key = os.environ["OPENAI_API_KEY"]
if os.path.isfile('config.yaml'):
    with open('config.yaml', 'r') as file:
        cfg = yaml.safe_load(file)
        openai.api_key = cfg["openapi_key"]

template = 'You are MedFact. Your task is to perform only one next action in the progress to check if the Observation SUPPORTS or REFUTES a Claim, or if there is NOT ENOUGH INFORMATION. Here are some examples:\nExample 1: Claim: Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.\nThought 1: MedFact needs to search Nikolaj Coster-Waldau and find if he has worked with the Fox Broadcasting Company.\nAction 1: Search[Nikolaj Coster-Waldau]\nObservation 1: Nikolaj William Coster-Waldau (born 27 July 1970) is a Danish actor and producer. He graduated from the Danish National School of Performing Arts in Copenhagen in 1993,[1] and had his breakthrough role in Denmark with the film Nightwatch (1994). He played Jaime Lannister in the HBO fantasy drama series Game of Thrones, for which he received two Primetime Emmy Award nominations for Outstanding Supporting Actor in a Drama Series.. Coster-Waldau has appeared in numerous films in his native Denmark and Scandinavia, including Headhunters (2011) and A Thousand Times Good Night (2013). In the U.S, his debut film role was in the war film Black Hawk Down (2001), playing Medal of Honor recipient Gary Gordon.[2] He then played a detective in the short-lived Fox television series New Amsterdam (2008), and appeared in the 2009 Fox television film Virtuality, originally intended as a pilot.\nThought 2: Because he appeared in the 2009 Fox television film Virtuality, he should have worked with the Fox Broadcasting Company.\nAction 2: Finish[SUPPORTS]\n\nExample 2: Claim: Stranger Things is set in Bloomington, Indiana.\nThought 1: MedFact needs to search for Stranger Things, and see if it is set in Bloomington, Indiana.\nAction 1: Search[Stranger Things]\nObservation 1: Stranger Things is an American science fiction horror drama television series created by the Duffer Brothers. Set in the 1980s, primarily in the fictional town of Hawkins, Indiana, the series centers on a number of mysteries and supernatural events occurring around the town and their impact on an ensemble of child and adult characters. \nThought 2: The observation says that it is set in a "fictional town of Hawkins, Indiana", so it is not set in Bloomington.\nAction 2: Finish[REFUTES]\n\nExample 3: Claim: Beautiful reached number two on the Billboard Hot 100 in 2003.?\nThought 1: MedFact needs to search the song Beautiful and find if it reached number two on the Billboard Hot 100 in 2003.\nAction 1: Search[Beautiful]\nObservation 1: Could not find [Beautiful]. Similar: [\'Beautiful\', \'Beautiful, Beautiful\', \'A Beautiful Mind (film)\', \'Beautiful (Christina Aguilera song)\', \'Life Is Beautiful\'].\nThought 2: From suggestions, MedFact needs to search "Beautiful (Christina Aguilera song)" to find the song.\nAction 2: Search[Beautiful (Christina Aguilera song)]\nObservation 2: "Beautiful" is a song recorded by American singer Christina Aguilera for her fourth studio album, Stripped (2002).\nThought 3: It does not mention Billboard, so MedFact needs to look up "Billboard Hot 100" to find if it reached number two on it in 2003.\nAction 3: Lookup[Billboard Hot 100]\nObservation 3: (Result 1 / 3) The song peaked at number two on the Billboard Hot 100 in the United States, where it was certified Gold for 500,000 units shipped.\nThought 4: It only says the song peaked at number two on the Billboard Hot 100, but not if it was in 2003. I am not sure if this claim is true or not.\nAction 4: Finish[NOT ENOUGH INFO]\n\n'

def llm_gpt4(prompt, model="gpt-4", stop=["\n"]):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def llm(prompt, stop=["\n"]):
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt,
      temperature=0,
      max_tokens=1000,
      top_p=1,
      frequency_penalty=0.0,
      presence_penalty=0.0,
      stop=stop
    )
    return response["choices"][0]["text"]

def step(env, action):
    attempts = 0
    while attempts < 10:
        try:
            return env.step(action)
        except requests.exceptions.Timeout:
            attempts += 1

def factCheck(claim, state = "", current_step = 0):

    if state == "":        
        state = "Claim: {}".format(claim)

    env = WikiEnv()
    env = FactCheckWrapper(env)        
    env.reset(state)

    i = current_step + 1
    prompt = template + state

    thought_action = llm(prompt + "\n" + f"Thought {i}:")

    try:
        # print(thought_action)
        thought, action = thought_action.strip().split(f"\nAction {i}: ")
    except:
        thought = thought_action.strip().split('\n')[0]
        # action = llm_gpt4(prompt + "\n" + f"Thought {i}: {thought}\nAction {i}:", stop=[f"\n"]).strip()
        action = llm(prompt + "\n" + f"Thought {i}: {thought}\nAction {i}:", stop=[f"\n"]).strip()
    
    obs, r, done, info = step(env, action[0].lower() + action[1:])
    obs = obs.replace('\\n', '')
    step_str = f"\nThought {i}: {thought}\nAction {i}: {action}\nObservation {i}: {obs}\n"
    state += step_str
    current_step += 1
    result = ""
    if done:
        result = action

    return format_answer(claim, state, current_step, done, result)

def format_answer(claim, state, current_step, done, result):
    lines = state.split("\n")
    lines = [p for p in lines if len(p) > 0]
    res = {}
    res["claim"] = claim
    res["current_step"] = current_step
    res["done"] = done
    evidence_tuples = []

    steps = []
    s = {}
    mode = "thought"

    for i in range(1, len(lines)):

        line = lines[i]

        if "Thought" in line:
            if mode == "observation":  #Next step found
                s["evidences"] = evidence_tuples
                steps.append(s)
                s = {}
                mode = "thought"
            
            s["thought"] = line.split(":")[1]
            mode = "action"
                
        if "Action" in line:
            assert mode == "action"
            s["action"] = line.split(":")[1]
            mode = "observation"

        if "Observation" in line:
            evidence_tuples = []

        if "Evidence" in line:
            evidence = {}
            evidence["content"] = line.split(":")[1]

        if "Source" in line:
            evidence["source"] = "".join(line.split(":")[1:])
            evidence_tuples.append(evidence)
    
    s["evidences"] = evidence_tuples
    steps.append(s)
    res["steps"] = steps
    res["state"] = state
    res["result"] = result
    return json.dumps(res)


if __name__ == "__main__":
    
    claim = "Creatine can cause abdominal cramp"
    res = factCheck(claim)
    # state, current_step, done = factCheck(claim)
    # # print(state)
    res = json.loads(res)
    res = factCheck(claim, res["state"], res["current_step"])
    print(res)
    
    # print(state)





