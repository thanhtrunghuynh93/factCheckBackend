from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def max_normalization(array):
    """
    Compute maximum normalization (max is set to 1) of the array
    :param array: 1-d array
    :return: 1-d array max- normalized : each value is multiplied by 1/max value
    """
    return 1/np.max(array) * array.squeeze(axis=1)

def get_aliases(kp_sim_between, candidates, threshold):
    """
    Find candidates which are very similar to the keyphrases (aliases)
    :param kp_sim_between: ndarray of shape (nb_kp , nb candidates) containing the similarity
    of each kp with all the candidates. Note that the similarity between the keyphrase and itself should be set to
    NaN or 0
    :param candidates: array of candidates (array of string)
    :return: list containing for each keyphrase a list that contain candidates which are aliases
    (very similar) (list of list of string)
    """

    kp_sim_between = np.nan_to_num(kp_sim_between, 0)
    idx_sorted = np.flip(np.argsort(kp_sim_between), 1)
    aliases = []
    for kp_idx, item in enumerate(idx_sorted):
        alias_for_item = []
        for i in item:
            if kp_sim_between[kp_idx, i] >= threshold:
                alias_for_item.append(candidates[i])
            else:
                break
        aliases.append(alias_for_item)

    return aliases

def _MMR(candidates, doc_embedd, X, N, beta=0.65, use_filtered=True, alias_threshold=0.8):
    """
    Returns:
    1)list of the top-N candidates (or less if there are not enough candidates) (list of string)
    2)list of associated relevance scores (list of float)
    3)list containing for each keyphrase a list of alias (list of list of string)
    """
    N = min(N, len(X))
    doc_sim = cosine_similarity(X, doc_embedd.reshape(1, -1))

    doc_sim_norm = doc_sim/np.max(doc_sim)
    doc_sim_norm = 0.5 + (doc_sim_norm - np.average(doc_sim_norm)) / np.std(doc_sim_norm)

    sim_between = cosine_similarity(X)
    np.fill_diagonal(sim_between, np.NaN)

    sim_between_norm = sim_between/np.nanmax(sim_between, axis=0)
    sim_between_norm = \
        0.5 + (sim_between_norm - np.nanmean(sim_between_norm, axis=0)) / np.nanstd(sim_between_norm, axis=0)

    selected_candidates = []
    unselected_candidates = [c for c in range(len(candidates))]

    j = np.argmax(doc_sim)
    selected_candidates.append(j)
    unselected_candidates.remove(j)

    for _ in range(N - 1):
        selec_array = np.array(selected_candidates)
        unselec_array = np.array(unselected_candidates)

        distance_to_doc = doc_sim_norm[unselec_array, :]
        dist_between = sim_between_norm[unselec_array][:, selec_array]
        if dist_between.ndim == 1:
            dist_between = dist_between[:, np.newaxis]
        j = np.argmax(beta * distance_to_doc - (1 - beta) * np.max(dist_between, axis=1).reshape(-1, 1))
        item_idx = unselected_candidates[j]
        selected_candidates.append(item_idx)
        unselected_candidates.remove(item_idx)

    # Not using normalized version of doc_sim for computing relevance
    relevance_list = max_normalization(doc_sim[selected_candidates]).tolist()
    aliases_list = get_aliases(sim_between[selected_candidates, :], candidates, alias_threshold)

    return candidates[selected_candidates].tolist(), relevance_list, aliases_list

