import numpy as np
from server.models.factCheck.mmr import _MMR

def get_diversed_evidences(model, claim, candidates, k=5, beta=0.8):
    candidate_embs = model.encode(candidates)
    candidate_embs = candidate_embs / np.linalg.norm(candidate_embs, axis=-1).reshape(-1, 1)
    query_emb = model.encode([claim])[0]
    query_emb = query_emb / np.linalg.norm(query_emb)

    diversed_candidates, relevance_list, aliases_list = _MMR(np.array(candidates), query_emb, candidate_embs, k, 
                                                             beta=beta,
                                                            alias_threshold=0.7)

    return diversed_candidates

def print_evidences(evidences):
    for i in range(len(evidences)):
        print("Evidences {}: {}\n".format(i+1, evidences[i]))

