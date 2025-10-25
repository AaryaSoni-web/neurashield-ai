import os
import sys
from typing import List, Dict, Optional
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
phase1_db = os.path.join(project_root, 'phase_1', 'chroma_db')

from phase_1.embedding_generator import EmbeddingGenerator
from phase_1.vector_store import ChromaVectorStore


class RAGCore:
    def __init__(self, vector_store: ChromaVectorStore, embedding_generator: EmbeddingGenerator, top_k: int = 5):
        self.vector_store = vector_store
        self.embedding_gen = embedding_generator
        self.top_k = top_k

    def retrieve_similar_patterns(self, query_code: str, top_k: Optional[int] = None,
                                  filter_by_type: Optional[str] = None) -> List[Dict]:
        k = top_k or self.top_k
        query_embedding = self.embedding_gen.generate_embedding(query_code)

        metadata_filter = None
        if filter_by_type:
            metadata_filter = {'type': filter_by_type}

        results = self.vector_store.search_similar_code(
            query_embedding=query_embedding,
            top_k=k,
            filter_metadata=metadata_filter
        )
        return results

    def format_context_for_prompt(self, similar_patterns: List[Dict], include_metadata: bool = True) -> str:
        context_parts = []

        for i, pattern in enumerate(similar_patterns, 1):
            similarity_score = pattern.get('similarity_score', 0)
            context_part = f"### Similar Pattern {i} (Similarity: {similarity_score:.2%})\n"

            if include_metadata:
                metadata = pattern['metadata']
                context_part += f"**File**: {metadata.get('file_path', 'unknown')}\n"
                context_part += f"**Type**: {metadata.get('type', 'unknown')}\n"
                context_part += f"**Name**: {metadata.get('name', 'unknown')}\n"
                context_part += f"**Lines**: {metadata.get('line_start', 0)}-{metadata.get('line_end', 0)}\n"

                if 'complexity_score' in metadata:
                    context_part += f"**Complexity Score**: {metadata.get('complexity_score')}\n"

            context_part += f"\n```{pattern['code']}```\n"
            context_parts.append(context_part)

        return "\n".join(context_parts)

    def build_rag_context(self, query_code: str, analysis_type: str = "bug_detection",
                         top_k: Optional[int] = None, filter_by_type: Optional[str] = None) -> Dict:
        similar_patterns = self.retrieve_similar_patterns(
            query_code=query_code,
            top_k=top_k,
            filter_by_type=filter_by_type
        )

        formatted_context = self.format_context_for_prompt(similar_patterns)

        return {
            'query_code': query_code,
            'retrieved_patterns': similar_patterns,
            'formatted_context': formatted_context,
            'analysis_type': analysis_type,
            'num_patterns': len(similar_patterns)
        }

    def save_context_to_file(self, context: Dict, output_file: str = "phase_2/rag_context.json"):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY environment variable")
        sys.exit(1)

    vector_store = ChromaVectorStore(
        collection_name="neurashield_code_v1",
        persist_directory=phase1_db
    )

    embedding_gen = EmbeddingGenerator()
    rag_core = RAGCore(vector_store=vector_store, embedding_generator=embedding_gen, top_k=3)

    test_code = """
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)
"""

    context = rag_core.build_rag_context(query_code=test_code, analysis_type="bug_detection", top_k=3)

    print(f"Retrieved {context['num_patterns']} patterns | Context length: {len(context['formatted_context'])} chars")
    rag_core.save_context_to_file(context)
    print("Context saved to phase_2/rag_context.json")