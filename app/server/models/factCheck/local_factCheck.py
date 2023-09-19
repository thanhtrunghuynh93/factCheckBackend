from server.models.factCheck.evidence_crawler import crawl_evidences
from server.models.factCheck.evidence_filter import get_diversed_evidences, print_evidences
from sentence_transformers import SentenceTransformer
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

import re
import json
import jellyfish
import openai
import yaml
from tqdm import tqdm
from collections import Counter

sbert = None 
model = None
tokenizer = None

PROMPT_TEMPLATE = """You are a bot that verifies the claim is true or not. Below is a claim and an evidence, classify if the evidence "Supports" or "Refutes" the claim, or "Not enough Info" to verify the claim. After classification, explain the reason for the answer.
Claim: {claim}
Evidence: {evidence}
Answer:"""

def initBert():
    global sbert
    sbert = SentenceTransformer('sentence-transformers/sentence-t5-base')

def initGenerativeModel():
    base_model = "tiiuae/falcon-7b"
    lora_weights = "thanhdath/falcon-7b-qlora-fever-answer-generation"

 #   base_model = "bigscience/bloom-3b"
  #  lora_weights = "thanhdath/bloom-3b-qlora-fever-answer-generation"
    global model
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        load_in_4bit=True,
        torch_dtype=torch.float32,
        trust_remote_code=True,
        device_map="auto",
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            llm_int8_threshold=6.0,
            llm_int8_has_fp16_weight=False,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type='nf4'
        ),
    )
    model = PeftModel.from_pretrained(
        model,
        lora_weights,
        torch_dtype=torch.float32,
    )
    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model.eval()
    return tokenizer, model


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

def format_answer(answers, evidences, evidence_url_dict):
    res = {}
    evidence_tuples = []

    nlis = []
    order = 1
    for i in range(1, len(answers)):
        evidence_tuple = {}
        
        evi, answer = answers[i-1].split("Answer:")
        evi = evi.replace("Evidence:", "").strip()
        expl = answer.strip()
        nli = answer.split('\n')[0].strip()
        nlis.append(nli)
        
        if evi in evidence_url_dict:
            url = evidence_url_dict[evi]
        else: 
            #GPT has shorten the evidence, find the original form in evidences
            original_evidence = find_most_matched(evi, evidences)
            url = evidence_url_dict[original_evidence]            
        
        evidence_tuple["order"] = order
        evidence_tuple["claim"] = evi
        evidence_tuple["explanation"] = expl
        evidence_tuple["source"] = url
        evidence_tuples.append(evidence_tuple)
        order += 1

    counter_nli = Counter(nlis)
    top_nlis = sorted(counter_nli.items(), key=lambda x: x[1], reverse=True)
    res["result"] = top_nlis[0][0]
    
    res["evidences"] = evidence_tuples
    
    return res

def verify_by_local_model(claim = "World-renowned singer Celine Dion died or revealed new personal health developments in late July 2023."):

    global sbert 
    if sbert is None: 
        initBert()

    global model
    global tokenizer
    if model is None:
        initGenerativeModel()

    candidates, candidate_url_dict = crawl_evidences(claim)
    evidences = get_diversed_evidences(sbert, claim, candidates, beta=0.7, k=10)
    print("\nEvidence list")
    print_evidences(evidences)

    answers = []
    for evidence in tqdm(evidences, desc="Analysis:"):
        prompt = PROMPT_TEMPLATE.format(claim=claim, evidence=evidence)
        inputs = tokenizer(prompt, return_tensors="pt")
        for k in inputs:
            inputs[k] = inputs[k].cuda()
        if 'token_type_ids' in inputs:
            del inputs['token_type_ids']
        with torch.no_grad():
            generation_output = model.generate(
                **inputs,
                temperature=0.2,
                top_p=0.75,
                top_k=100,
                output_scores=False,
                max_new_tokens=128,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id
            )

            output = tokenizer.decode(generation_output[0], skip_special_tokens=True).strip()
            answer = output.split("Evidence:")[-1].strip()

            answer = "Evidence:" + answer

        answers.append(answer)

    return format_answer(answers, candidates, candidate_url_dict)

if __name__ == "__main__":
    
    verify()


