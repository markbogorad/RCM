from collections import Counter
import re

def clean_and_tokenize(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if len(w) > 2]

def compute_word_frequencies(text_blocks, top_n=20):
    all_tokens = []
    for block in text_blocks:
        all_tokens.extend(clean_and_tokenize(block))
    return Counter(all_tokens).most_common(top_n)

def generate_metrics_summary(emails_found, sources_scanned, avg_score):
    return {
        "Emails Found": emails_found,
        "Sources Scanned": sources_scanned,
        "Average Semantic Score": round(avg_score, 4) if avg_score else "N/A"
    }

def render_summary_table(st, metrics_dict):
    for key, value in metrics_dict.items():
        st.markdown(f"**{key}**: {value}")
