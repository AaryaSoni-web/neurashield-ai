import chromadb
from typing import List, Dict, Optional
import json
import os


class ChromaVectorStore:
    def __init__(self, collection_name: str = "neurashield_code", persist_directory: str = "./chroma_db"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "NeuraShield code embeddings for RAG analysis"}
        )

    def upsert_chunks(self, chunks: List[Dict], batch_size: int = 100):
        total_upserted = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            ids = []
            embeddings = []
            documents = []
            metadatas = []

            for idx, chunk in enumerate(batch):
                chunk_id = f"{chunk.get('file_path', 'unknown')}_{chunk.get('name', f'chunk_{idx}')}"
                chunk_id = chunk_id.replace('/', '_').replace('.', '_')
                ids.append(chunk_id)

                if 'embedding' not in chunk:
                    continue

                embeddings.append(chunk['embedding'])
                documents.append(chunk['code'])

                metadata = {
                    'file_path': str(chunk.get('file_path', '')),
                    'type': str(chunk.get('type', 'unknown')),
                    'name': str(chunk.get('name', '')),
                    'line_start': int(chunk.get('line_start', 0)),
                    'line_end': int(chunk.get('line_end', 0)),
                    'token_count': int(chunk.get('token_count', 0)),
                    'language': str(chunk.get('language', 'python'))
                }

                if 'file_metadata' in chunk:
                    file_meta = chunk['file_metadata']
                    metadata['complexity_score'] = int(file_meta.get('complexity_score', 0))
                    metadata['file_loc'] = int(file_meta.get('loc', 0))

                if 'class_name' in chunk:
                    metadata['class_name'] = str(chunk['class_name'])
                if 'is_async' in chunk:
                    metadata['is_async'] = str(chunk['is_async'])

                metadatas.append(metadata)

            if embeddings:
                self.collection.upsert(
                    ids=ids[:len(embeddings)],
                    embeddings=embeddings,
                    documents=documents[:len(embeddings)],
                    metadatas=metadatas[:len(embeddings)]
                )
                total_upserted += len(embeddings)

        return total_upserted

    def search_similar_code(self, query_embedding: List[float], top_k: int = 5,
                           filter_metadata: Optional[Dict] = None) -> List[Dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata if filter_metadata else None
        )

        similar_chunks = []
        for i in range(len(results['ids'][0])):
            similar_chunks.append({
                'id': results['ids'][0][i],
                'similarity_score': 1 - results['distances'][0][i],
                'code': results['documents'][0][i],
                'metadata': results['metadatas'][0][i]
            })

        return similar_chunks

    def search_by_text(self, query_text: str, embedding_generator, top_k: int = 5,
                      filter_metadata: Optional[Dict] = None) -> List[Dict]:
        query_embedding = embedding_generator.generate_embedding(query_text)
        return self.search_similar_code(query_embedding, top_k=top_k, filter_metadata=filter_metadata)

    def get_stats(self) -> Dict:
        total_count = self.collection.count()

        if total_count == 0:
            return {
                'total_chunks': 0,
                'collection_name': self.collection_name,
                'type_distribution': {},
                'top_files': []
            }

        sample = self.collection.get()
        type_counts = {}
        file_counts = {}

        for metadata in sample['metadatas']:
            chunk_type = metadata.get('type', 'unknown')
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1

            file_path = metadata.get('file_path', 'unknown')
            file_counts[file_path] = file_counts.get(file_path, 0) + 1

        return {
            'total_chunks': total_count,
            'collection_name': self.collection_name,
            'type_distribution': type_counts,
            'top_files': sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        }

    def clear_collection(self):
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(name=self.collection_name)

    def load_and_store_embeddings(self, embeddings_file: str = 'phase_1/embeddings.json'):
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        total = self.upsert_chunks(chunks)
        print(f"Stored {total} chunks in ChromaDB")


if __name__ == "__main__":
    vector_store = ChromaVectorStore(
        collection_name="neurashield_code",
        persist_directory="phase_1/chroma_db"
    )

    vector_store.load_and_store_embeddings(embeddings_file='phase_1/embeddings.json')