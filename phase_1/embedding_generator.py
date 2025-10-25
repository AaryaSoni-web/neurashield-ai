
import os
import json
from openai import OpenAI
from typing import List, Dict
import time


class EmbeddingGenerator:
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.dimensions = 1536 if "small" in model else 3072

    def generate_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(input=text, model=self.model)
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Error generating embedding: {e}")

    def generate_batch_embeddings(self, chunks: List[Dict], batch_size: int = 100, 
                                  delay_seconds: float = 0.1) -> List[Dict]:
        total_chunks = len(chunks)
        enriched_chunks = []

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]

            try:
                texts = [chunk['code'] for chunk in batch]
                response = self.client.embeddings.create(input=texts, model=self.model)

                for chunk, embedding_obj in zip(batch, response.data):
                    chunk['embedding'] = embedding_obj.embedding
                    chunk['embedding_model'] = self.model
                    chunk['embedding_dimensions'] = len(embedding_obj.embedding)
                    enriched_chunks.append(chunk)

                if i + batch_size < total_chunks:
                    time.sleep(delay_seconds)

            except Exception:
                continue

        return enriched_chunks

    def estimate_cost(self, total_tokens: int) -> Dict:
        cost_per_million = 0.02 if "small" in self.model else 0.13
        estimated_cost = (total_tokens / 1_000_000) * cost_per_million

        return {
            'model': self.model,
            'total_tokens': total_tokens,
            'cost_per_million_tokens': f"${cost_per_million}",
            'estimated_cost_usd': f"${estimated_cost:.4f}"
        }

    def generate_embeddings_from_file(self, input_file: str = 'phase_1/chunked_code.json',
                                     output_file: str = 'phase_1/embeddings.json',
                                     batch_size: int = 100):
        with open(input_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        total_tokens = sum(chunk.get('token_count', 0) for chunk in chunks)
        cost_estimate = self.estimate_cost(total_tokens)

        print(f"Tokens: {cost_estimate['total_tokens']:,} | Estimated cost: {cost_estimate['estimated_cost_usd']}")

        enriched_chunks = self.generate_batch_embeddings(chunks, batch_size=batch_size)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_chunks, f, indent=2)

        print(f"Generated {len(enriched_chunks)} embeddings -> {output_file}")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY environment variable")
        print("Get key from: https://platform.openai.com/api-keys")
        exit(1)

    generator = EmbeddingGenerator(model="text-embedding-3-small")
    generator.generate_embeddings_from_file(
        input_file='phase_1/chunked_code.json',
        output_file='phase_1/embeddings.json',
        batch_size=100
    )