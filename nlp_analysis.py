from collections import Counter
import spacy

_NLP = spacy.load("en_core_web_sm")

def collectnodes(node):
    nodes = [node]
    links = node.get("links")
    if links is not None:
        for child in links:
            nodes.extend(collectnodes(child))
    return nodes

def analyze_tree(root_node, top_n=30):
    all_nodes = collectnodes(root_node)

    word_counter = Counter()
    person_counter = Counter()
    place_counter = Counter()

    for node in all_nodes:
        text = node.get("content", "") or ""
        doc = _NLP(text)

        for tok in doc:
            if tok.is_alpha and not tok.is_stop:
                lemma = tok.lemma_.lower()
                word_counter[lemma] += 1

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                person_counter[ent.text] += 1
            elif ent.label_ == "GPE":
                place_counter[ent.text] += 1

    return {
        "top_words": word_counter.most_common(top_n),
        "top_person_entities": person_counter.most_common(top_n),
        "top_place_entities": place_counter.most_common(top_n)
    }
