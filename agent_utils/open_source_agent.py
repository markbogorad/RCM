import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

class OpenSourceAgent:
    def __init__(self, system_message, data=None, model_name="PleIAs/Pleias-RAG-1B"):
        self.system_message = system_message
        self.data = data  # DataFrame or other context for RAG
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=-1
        )

    def generate_response(self, user_input):
        # Prepare sources from the data (for RAG)
        sources = []
        if self.data is not None:
            # For demonstration, use the first 3 rows as sources
            for i, row in self.data.head(3).iterrows():
                # Combine relevant fields into a text chunk
                text = ", ".join([f"{col}: {row[col]}" for col in self.data.columns if pd.notna(row[col])])
                sources.append({"text": text, "metadata": {"row": i}})

        # Build the prompt in Pleias-RAG-1B style
        prompt = f"System: {self.system_message}\n"
        prompt += f"Query: {user_input}\n"
        if sources:
            prompt += "Sources:\n"
            for idx, src in enumerate(sources):
                prompt += f"[{idx+1}] {src['text']}\n"
        prompt += "Answer:"

        # Generate response
        output = self.generator(prompt, max_new_tokens=256, do_sample=True, temperature=0.7)[0]["generated_text"]
        # Extract only the answer part
        answer = output.split("Answer:", 1)[-1].strip()
        return answer 