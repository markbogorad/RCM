from sentence_transformers import SentenceTransformer, util

# Load SBERT model once
_model = SentenceTransformer("all-MiniLM-L6-v2")

# Centralized domain reference phrases (editable in one place only)
_REFERENCE_PHRASES = [
    "wealth management",
    "institutional sales",
    "private client advisor",
    "financial advisor",
    "portfolio construction",
    "alternative investments"
]

def get_model():
    return _model

def get_reference_phrases():
    return _REFERENCE_PHRASES

def get_reference_embeddings():
    return _model.encode(_REFERENCE_PHRASES, convert_to_tensor=True)

def embed_text(text):
    return _model.encode(text, convert_to_tensor=True)

def semantic_score(text, reference_embeddings=None):
    if reference_embeddings is None:
        reference_embeddings = get_reference_embeddings()
    embedding = embed_text(text)
    cosine_scores = util.cos_sim(embedding, reference_embeddings)
    return float(cosine_scores.max())
