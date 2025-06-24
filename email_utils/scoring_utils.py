from email_utils.semantic_utils import embed_text, semantic_score

def score_candidates(email_contexts, reference_embeddings):
    results = []
    for email, context in email_contexts:
        try:
            score = semantic_score(context, reference_embeddings)
            results.append((email, context, score))
        except Exception:
            continue
    return sorted(results, key=lambda x: x[2], reverse=True)

def combine_confidence(semantic_score, pattern_match=False, source_rank=None):
    base = semantic_score
    if pattern_match:
        base += 0.1
    if source_rank is not None:
        base += max(0, 0.1 - 0.01 * source_rank)
    return round(min(base, 1.0), 4)

def summarize_hits(scored_emails):
    if not scored_emails:
        return {}
    scores = [score for _, _, score in scored_emails]
    return {
        "num_emails": len(scored_emails),
        "avg_score": sum(scores) / len(scores),
        "top_score": max(scores),
        "min_score": min(scores)
    }
