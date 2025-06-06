import torch
from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer("all-MiniLM-L6-v2")
target_sentences = [
    "investment strategy research",
    "wealth management insights",
    "contact head of research or CIO",
    "private client portfolio management"
    "gatekeeper"
]
target_embedding = model.encode(target_sentences, convert_to_tensor=True)

def semantic_score(text: str) -> float:
    try:
        embedding = model.encode(text, convert_to_tensor=True)
        score = util.cos_sim(embedding, target_embedding).mean().item()
        return round(score, 4)
    except Exception as e:
        print(f"Embedding failed: {e}")
        return 0.0
