from server.models.factCheck.evidence_crawler import crawl_evidences
from server.models.factCheck.evidence_filter import get_diversed_evidences, print_evidences
from sentence_transformers import SentenceTransformer

import json
import jellyfish
import openai
import yaml
import os

sbert = None 

if os.path.isfile('config.yaml'):
    with open('config.yaml', 'r') as file:
        cfg = yaml.safe_load(file)
        openai.api_key = cfg["openapi_key"]

def initBert():
    global sbert
    sbert = SentenceTransformer('sentence-transformers/sentence-t5-base')

def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def generate_prompt(claim, evidences):
    prompt = "Act as a journalist, justify the claim given the evidences. Write only the answer in [Fake, True] in the first line. Then, point out the most 5 relevant evidences leading to the conclusion with the format: [Original evidence number]: '''[Original evidence]'''. Explanation: [explanation]."
    prompt += "\nClaim: '''{}'''".format(claim)
    prompt += "\nEvidences:\n"
    for i in range(len(evidences)): 
        prompt += "{}.'''{}'''\n".format(i + 1, evidences[i])

    prompt += "Example: \nTrue\n1: '''Qatar's Sheikh Jassim bin Hamad Al Thani has won the race to buy Manchester United'''. Explanation: This indicates that Sheikh Jassim bin Hamad Al Thani has emerged as the winner in the race.".format(claim)    
        
    return prompt

def find_most_matched(input_evidence, evidences):
    most_matched = evidences[0]
    most_matched_score = 0
    
    for evis in evidences: 
        score = jellyfish.levenshtein_distance(input_evidence, evis)
        if score > most_matched_score:
            most_matched_score = score
            most_matched = evis
    
    return most_matched    

# def format_answer(answer, evidences, evidence_url_dict):
#     lines = answer.split("\n")
#     answer = "The fact is: {}".format(lines[0])
#     for i in range(1, len(lines)):
        
#         es = lines[i].split("\"")
#         if len(es) != 3:
#             break
#         evi = es[1]
#         expl = es[2]
        
#         if evi in evidence_url_dict:
#             url = evidence_url_dict[evi]
#         else: 
#             #GPT has shorten the evidence, find the original form in evidences
#             original_evidence = find_most_matched(evi, evidences)
#             url = evidence_url_dict[original_evidence]            
        
#         answer += "\nEvidence {}: {}\nExplanation: {}\nSource: {}\n".format(i, evi, expl, url)
    
#     return answer

def format_answer(answer, evidences, evidence_url_dict):
    lines = answer.split("\n")
    res = {}
    res["result"] = lines[0]
    evidence_tuples = []

    order = 1
    
    for i in range(1, len(lines)):
        evidence_tuple = {}
        
        es = lines[i].split("'''")
        if len(es) != 3:
            print(es)
            continue
        evi = es[1]
        expl = es[2]
        
        if evi in evidence_url_dict:
            url = evidence_url_dict[evi]
        else: 
            #GPT has shorten the evidence, find the original form in evidences
            original_evidence = find_most_matched(evi, evidences)
            url = evidence_url_dict[original_evidence]            
        
        evidence_tuple["order"] = order
        evidence_tuple["claim"] = evi
        evidence_tuple["explanation"] = expl.split("Explanation:")[1]
        evidence_tuple["source"] = url
        evidence_tuples.append(evidence_tuple)
        order += 1
    
    res["evidences"] = evidence_tuples
    
    return json.dumps(res)

def verify_gpt(claim = "World-renowned singer Celine Dion died or revealed new personal health developments in late July 2023."):

    global sbert 
    if sbert is None: 
        initBert()

    candidates, candidate_url_dict = crawl_evidences(claim)
    evidences = get_diversed_evidences(sbert, claim, candidates, beta=0.7, k=10)
    print("\nEvidence list")
    print_evidences(evidences)
    prompt = generate_prompt(claim, evidences)
    print("\nAnalysis")
    answer = get_completion(prompt)
    print(answer)
    return format_answer(answer, candidates, candidate_url_dict)

if __name__ == "__main__":
    
    verify_gpt()


