import os
import sys
from typing import Dict, Optional, List
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase_2.rag_core import RAGCore
from phase_2.llm_analyzer import LLMAnalyzer
from phase_1.vector_store import ChromaVectorStore
from phase_1.embedding_generator import EmbeddingGenerator


class RAGAnalyzer:
    def __init__(self, vector_store: ChromaVectorStore, embedding_generator: EmbeddingGenerator,
                 llm_model: str = "gpt-4o", top_k: int = 5):
        self.rag_core = RAGCore(
            vector_store=vector_store,
            embedding_generator=embedding_generator,
            top_k=top_k
        )
        self.llm_analyzer = LLMAnalyzer(model=llm_model)

    def analyze_code(self, code: str, analysis_type: str = "all", top_k: Optional[int] = None) -> Dict:
        max_retries = 2
        last_error = None
        for attempt in range(max_retries):
            try:
                timestamp = datetime.now().isoformat()

                rag_context = self.rag_core.build_rag_context(
                    query_code=code,
                    analysis_type=analysis_type,
                    top_k=top_k
                )

                results = {
                    'timestamp': timestamp,
                    'code': code,
                    'analysis_type': analysis_type,
                    'retrieved_patterns_count': rag_context['num_patterns'],
                    'retrieved_patterns': rag_context['retrieved_patterns']
                }

                if analysis_type in ['bugs', 'all']:
                    bug_analysis = self.llm_analyzer.analyze_for_bugs(
                        query_code=code,
                        retrieved_context=rag_context['formatted_context']
                    )
                    results['bug_analysis'] = bug_analysis

                if analysis_type in ['optimization', 'all']:
                    optimization_analysis = self.llm_analyzer.analyze_for_optimization(
                        query_code=code,
                        retrieved_context=rag_context['formatted_context']
                    )
                    results['optimization_analysis'] = optimization_analysis

                if analysis_type in ['security', 'all']:
                    security_analysis = self.llm_analyzer.calculate_security_score(
                        query_code=code,
                        retrieved_context=rag_context['formatted_context']
                    )
                    results['security_analysis'] = security_analysis

                return results
            except TimeoutError as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"⚠️ Timeout on attempt {attempt + 1}, retrying...")
                    continue
            except Exception as e:
                return {
                    'error': f'Analysis failed: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
        
        return {
            'error': f'Analysis timed out after {max_retries} attempts',
            'timestamp': datetime.now().isoformat()
        }

    def batch_analyze(self, code_samples: List[Dict], analysis_type: str = "all") -> List[Dict]:
        results = []
        for i, sample in enumerate(code_samples, 1):
            analysis = self.analyze_code(code=sample['code'], analysis_type=analysis_type)
            analysis['sample_name'] = sample.get('name', f"sample_{i}")
            results.append(analysis)
        return results

    def generate_report(self, analysis_results: Dict) -> str:
        report_lines = []
        report_lines.append("="*70)
        report_lines.append("NEURASHIELD.AI - CODE ANALYSIS REPORT")
        report_lines.append("="*70)
        report_lines.append(f"Timestamp: {analysis_results['timestamp']}")
        report_lines.append(f"Analysis Type: {analysis_results['analysis_type']}")
        report_lines.append(f"Retrieved Patterns: {analysis_results['retrieved_patterns_count']}")
        report_lines.append(f"Code Length: {len(analysis_results['code'])} characters")
        report_lines.append("\n" + "-"*70)

        if 'bug_analysis' in analysis_results:
            bug_data = analysis_results['bug_analysis']
            report_lines.append("\n## BUG DETECTION")
            report_lines.append("-"*70)

            if bug_data.get('error'):
                report_lines.append(f"✗ Error: {bug_data['error']}")
            elif bug_data.get('has_bugs', False):
                bugs = bug_data.get('bugs_found', [])
                report_lines.append(f"⚠️  BUGS FOUND: {len(bugs)}")
                report_lines.append(f"Overall Risk: {bug_data.get('overall_risk', 'unknown').upper()}")

                for i, bug in enumerate(bugs, 1):
                    report_lines.append(f"\n{i}. {bug['type']} (Severity: {bug['severity'].upper()})")
                    report_lines.append(f"   Line: {bug['line']}")
                    report_lines.append(f"   Description: {bug['description']}")
                    report_lines.append(f"   Exploit Difficulty: {bug['exploit_difficulty']}")

                    impact = bug.get('impact', {})
                    report_lines.append(f"   Impact: C:{impact.get('confidentiality', 'N/A')} "
                                      f"I:{impact.get('integrity', 'N/A')} "
                                      f"A:{impact.get('availability', 'N/A')}")

                    fix = bug.get('fix', 'No fix provided')
                    report_lines.append(f"   Fix: {fix[:200]}...")

                    if 'cwe_id' in bug:
                        report_lines.append(f"   CWE: {bug['cwe_id']}")
            else:
                report_lines.append("✓ No bugs detected")

        if 'optimization_analysis' in analysis_results:
            opt_data = analysis_results['optimization_analysis']
            report_lines.append("\n\n## CODE OPTIMIZATION")
            report_lines.append("-"*70)

            if opt_data.get('error'):
                report_lines.append(f"✗ Error: {opt_data['error']}")
            else:
                complexity = opt_data.get('current_complexity', {})
                report_lines.append(f"Current Complexity:")
                report_lines.append(f"  Time: {complexity.get('time', 'unknown')}")
                report_lines.append(f"  Space: {complexity.get('space', 'unknown')}")

                bottlenecks = complexity.get('bottlenecks', [])
                if bottlenecks:
                    report_lines.append(f"  Bottlenecks: {', '.join(bottlenecks)}")

                optimizations = opt_data.get('optimizations', [])
                if optimizations:
                    report_lines.append(f"\n⚡ OPTIMIZATIONS FOUND: {len(optimizations)}")
                    report_lines.append(f"Estimated Speedup: {opt_data.get('estimated_speedup', 'N/A')}")

                    for i, opt in enumerate(optimizations, 1):
                        report_lines.append(f"\n{i}. {opt['type'].upper()}: {opt['description']}")
                        report_lines.append(f"   Improvement: {opt.get('improvement', 'N/A')}")
                        if 'trade_offs' in opt:
                            report_lines.append(f"   Trade-offs: {opt['trade_offs']}")
                else:
                    report_lines.append("\n✓ Code is well-optimized")

        if 'security_analysis' in analysis_results:
            sec_data = analysis_results['security_analysis']
            report_lines.append("\n\n## SECURITY SCORING (CVSS v3.1)")
            report_lines.append("-"*70)

            if sec_data.get('error'):
                report_lines.append(f"✗ Error: {sec_data['error']}")
            else:
                score = sec_data.get('overall_security_score', 0)
                severity = sec_data.get('overall_severity', 'Unknown')

                report_lines.append(f"Overall Security Score: {score}/10")
                report_lines.append(f"Severity: {severity.upper()}")

                risk_summary = sec_data.get('risk_summary', 'No summary available')
                report_lines.append(f"\nRisk Summary:")
                report_lines.append(f"  {risk_summary}")

                vulnerabilities = sec_data.get('vulnerabilities', [])
                if vulnerabilities:
                    report_lines.append(f"\n🛡️  VULNERABILITIES: {len(vulnerabilities)}")
                    for i, vuln in enumerate(vulnerabilities, 1):
                        report_lines.append(f"\n{i}. {vuln['type']}")
                        report_lines.append(f"   CVSS Score: {vuln.get('cvss_score', 'N/A')}")
                        report_lines.append(f"   CVSS Vector: {vuln.get('cvss_vector', 'N/A')}")
                        report_lines.append(f"   CWE: {vuln.get('cwe_id', 'N/A')}")
                        report_lines.append(f"   Remediation: {vuln.get('remediation', 'N/A')[:150]}...")

                immediate_actions = sec_data.get('immediate_actions', [])
                if immediate_actions:
                    report_lines.append(f"\nImmediate Actions Required:")
                    for action in immediate_actions:
                        report_lines.append(f"  • {action}")

        report_lines.append("\n" + "="*70)
        report_lines.append("END OF REPORT")
        report_lines.append("="*70)

        return "\n".join(report_lines)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY environment variable")
        sys.exit(1)

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
        top_k=3
    )

    test_code = """def process_user_input(user_id, data):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = database.execute(query)

    output = []
    for i in range(len(data)):
        output.append(data[i] * 2)

    return result, output"""

    results = analyzer.analyze_code(code=test_code, analysis_type="all")
    report = analyzer.generate_report(results)

    output_dir = "phase_2"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'analysis_results.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(os.path.join(output_dir, 'analysis_report.txt'), 'w', encoding='utf-8') as f:
        f.write(report)

    print("Analysis complete. Results saved to phase_2/")