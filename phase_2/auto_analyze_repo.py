
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase1_pipeline import GITHUB_REPO_URL
from phase_1.vector_store import ChromaVectorStore
from phase_1.embedding_generator import EmbeddingGenerator
from phase_1.code_extractor import GitHubCodeExtractor
from phase_2.rag_analyzer import RAGAnalyzer


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    phase1_db = os.path.join(project_root, 'phase_1', 'chroma_db')

    vector_store = ChromaVectorStore(
        collection_name="neurashield_code_v1",
        persist_directory=phase1_db
    )
    embedding_gen = EmbeddingGenerator()

    analyzer = RAGAnalyzer(
        vector_store=vector_store,
        embedding_generator=embedding_gen,
        llm_model="gpt-4o",
        top_k=5
    )

    extractor = GitHubCodeExtractor(GITHUB_REPO_URL)
    code_files = extractor.extract_python_files()

    print(f"Analyzing {len(code_files)} files from {GITHUB_REPO_URL}")

    samples = [
        {'code': data['source_code'], 'name': data['file_path']}
        for data in code_files
    ]

    results = analyzer.batch_analyze(code_samples=samples, analysis_type='all')

    output_json = os.path.join(project_root, 'phase_2', 'repo_analysis_results.json')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    report_txt = os.path.join(project_root, 'phase_2', 'repo_analysis_report.txt')
    with open(report_txt, 'w', encoding='utf-8') as f:
        for file_result in results:
            report = analyzer.generate_report(file_result)
            f.write(report + "\n\n" + "-"*70 + "\n\n")

    extractor.cleanup()

    print(f"Analysis complete. Results saved to phase_2/")


if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY environment variable")
        sys.exit(1)
    main()