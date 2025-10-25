
from vector_store import ChromaVectorStore
from embedding_generator import EmbeddingGenerator


vector_store = ChromaVectorStore(persist_directory="phase_1/chroma_db")
generator = EmbeddingGenerator()

results = vector_store.search_by_text("multiply matrices", generator, top_k=3)

for i, result in enumerate(results, 1):
    print(f"{i}. {result['metadata']['name']} | {result['metadata']['file_path']} | Score: {result['similarity_score']:.3f}")