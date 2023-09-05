from server.models.factCheck.evidence_crawler import crawl_evidences
from server.models.factCheck.evidence_filter import get_diversed_evidences, print_evidences
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, AutoTokenizer

import torch
import json
import jellyfish
import yaml

nli_model= None
tokenizer_model= None
sbert = None
nli_labels = ['contradiction', 'neutral', 'entailment']
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def initModels(nli= "facebook/bart-large-mnli", tokenizer= "facebook/bart-large-mnli"):
    global nli_model, tokenizer_model, sbert
    nli_model = AutoModelForSequenceClassification.from_pretrained(nli).to(device)
    tokenizer_model= AutoTokenizer.from_pretrained(tokenizer)
    sbert = SentenceTransformer('sentence-transformers/sentence-t5-base')


def process_nli(claim, evidences):
    global nli_model, tokenizer_model, sbert
    res = {}
    evidence_tuples = []
    num_contradiction = 0
    num_neutral = 0
    num_entailment = 0
    order = 1
    for evis in evidences:
        evidence_tuple = {}
        # print(e)
        premise = evis
        hypothesis = claim
        # run through model pre-trained on MNLI
        x = tokenizer_model.encode(premise, hypothesis, return_tensors='pt',
                             truncation_strategy='only_first')
        logits = nli_model(x.to(device))[0]
        entail_contradiction_logits = logits
        probs = entail_contradiction_logits.softmax(dim=1)
        nli_labels_argmax = nli_labels[torch.argmax(probs)]
        if nli_labels_argmax == "contradiction":
            num_contradiction += 1
        elif nli_labels_argmax == "neutral":
            num_neutral += 1
        elif nli_labels_argmax == "entailment":
            num_entailment += 1
        evidence_tuple["order"] = order
        evidence_tuple["claim"] = premise
        evidence_tuple["nli_label"] = nli_labels_argmax
        evidence_tuple["probs"] = probs.detach().cpu().numpy().tolist()
        evidence_tuples.append(evidence_tuple)
        order += 1
    if num_entailment > num_contradiction:
        result = True
    elif num_entailment < num_contradiction:
        result = False
    else:
        result = 'unknown'


    res["result"] = result
    res["evidences"] = evidence_tuples
    res["num_entailment"] = num_entailment
    res["num_contradiction"] = num_contradiction
    res["num_neutral"] = num_neutral
    return res


def verify(claim = "World-renowned singer Celine Dion died or revealed new personal health developments in late July 2023."):

    global nli_model, tokenizer_model, sbert
    if nli_model is None or tokenizer_model is None or sbert is None:
        initModels()

    candidates, candidate_url_dict = crawl_evidences(claim)
    evidences = get_diversed_evidences(sbert, claim, candidates, beta=0.7, k=10)
    print("\nEvidence list")
    print_evidences(evidences)
    print("\nAnalysis")
    res = process_nli(claim, evidences)
    print(res)
    return json.dumps(res)

if __name__ == "__main__":
    
    verify()


