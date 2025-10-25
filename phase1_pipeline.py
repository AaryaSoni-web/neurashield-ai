"""
    Other test repositories:
    https://github.com/ubc/flask-sample-app
    https://github.com/ericsalesdeandrade/pytest-github-actions-example
    https://github.com/ginomempin/sample-ci-python
    https://github.com/gabicavalcante/django-test-ci
    https://github.com/sea-bass/python-testing-ci
"""
GITHUB_REPO_URL = "https://github.com/ubc/flask-sample-app"

import os
import sys
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'phase_1'))
from phase_1.code_extractor import GitHubCodeExtractor
from phase_1.code_preprocessor import CodePreprocessor
from phase_1.code_chunker import CodeChunker
from phase_1.embedding_generator import EmbeddingGenerator
from phase_1.vector_store import ChromaVectorStore


class Phase1Pipeline:
    def __init__(self, repo_url: str, openai_api_key: str = None, collection_name: str = "neurashield_code"):
        self.repo_url = repo_url
        self.extractor = GitHubCodeExtractor(repo_url)
        self.preprocessor = CodePreprocessor()
        self.chunker = CodeChunker()
        self.embedding_gen = EmbeddingGenerator(api_key=openai_api_key)
        self.vector_store = ChromaVectorStore(
            collection_name=collection_name,
            persist_directory="phase_1/chroma_db"
        )

    def run_pipeline(self, remove_comments: bool = True, max_tokens_per_chunk: int = 500, 
                    batch_size: int = 100) -> Dict:
        stats = {'repo_url': self.repo_url, 'files_extracted': 0, 'chunks_created': 0, 
                'embeddings_generated': 0, 'stored_in_db': 0}

        code_files = self.extractor.extract_python_files()
        stats['files_extracted'] = len(code_files)

        if not code_files:
            return stats

        for file_data in code_files:
            result = self.preprocessor.preprocess(file_data['source_code'], remove_comments=remove_comments)
            file_data['cleaned_code'] = result['cleaned_code']
            file_data['complexity_score'] = result['complexity_score']
            file_data['reduction_percentage'] = result['reduction_percentage']

        all_chunks = []
        for file_data in code_files:
            chunks = self.chunker.chunk_by_function(
                file_data['cleaned_code'], file_data['file_path'], max_tokens=max_tokens_per_chunk
            )
            for chunk in chunks:
                chunk['file_metadata'] = {
                    'complexity_score': file_data['complexity_score'],
                    'loc': file_data['loc'],
                    'functions': file_data.get('functions', []),
                    'classes': file_data.get('classes', []),
                    'imports': file_data.get('imports', [])
                }
                chunk['language'] = 'python'
            all_chunks.extend(chunks)

        stats['chunks_created'] = len(all_chunks)

        total_tokens = sum(chunk['token_count'] for chunk in all_chunks)
        cost_estimate = self.embedding_gen.estimate_cost(total_tokens)
        print(f"Tokens: {total_tokens:,} | Cost: {cost_estimate['estimated_cost_usd']}")

        enriched_chunks = self.embedding_gen.generate_batch_embeddings(all_chunks, batch_size=batch_size)
        stats['embeddings_generated'] = len(enriched_chunks)

        self.vector_store.upsert_chunks(enriched_chunks)
        stats['stored_in_db'] = self.vector_store.collection.count()

        print(f"Pipeline complete: {stats['files_extracted']} files | {stats['chunks_created']} chunks | {stats['stored_in_db']} in DB")
        return stats

    def cleanup(self):
        self.extractor.cleanup()


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY environment variable")
        exit(1)

    pipeline = Phase1Pipeline(repo_url=GITHUB_REPO_URL, collection_name="neurashield_code_v1")

    try:
        stats = pipeline.run_pipeline(remove_comments=True, max_tokens_per_chunk=500, batch_size=50)
        print("Phase 1 complete. Run query_code.py to test.")
    except KeyboardInterrupt:
        print("\nPipeline interrupted")
    except Exception as e:
        print(f"Pipeline failed: {e}")
    finally:
        pipeline.cleanup()