
import os
import sys
from openai import OpenAI
from typing import Dict, Optional
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase_2.prompt_templates import PromptTemplates
from phase_2.rag_core import RAGCore
from phase_1.embedding_generator import EmbeddingGenerator
from phase_1.vector_store import ChromaVectorStore


class LLMAnalyzer:
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.3, max_tokens: int = 2000, 
                 api_key: Optional[str] = None):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=api_key)
        self.prompt_templates = PromptTemplates()

    def _call_llm(self, system_prompt: str, user_prompt: str, response_format: str = "json_object") -> Dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": response_format} if response_format == "json_object" else None
            )

            content = response.choices[0].message.content
            usage = response.usage
            cost_info = self.estimate_cost(usage.prompt_tokens, usage.completion_tokens)

            print(f"Tokens: {usage.total_tokens} | Cost: {cost_info['total_cost_usd']}")

            if response_format == "json_object":
                return json.loads(content)
            return {"response": content}

        except json.JSONDecodeError as e:
            return {"error": "Invalid JSON response", "raw_content": content}
        except Exception as e:
            return {"error": str(e)}

    def analyze_for_bugs(self, query_code: str, retrieved_context: str) -> Dict:
        prompt = self.prompt_templates.render_bug_detection_prompt(
            query_code=query_code,
            context=retrieved_context
        )

        result = self._call_llm(
            system_prompt=prompt['system'],
            user_prompt=prompt['user'],
            response_format="json_object"
        )

        if "error" not in result:
            bug_count = len(result.get('bugs_found', []))
            risk_level = result.get('overall_risk', 'unknown')
            print(f"Bugs: {bug_count} | Risk: {risk_level.upper()}")

        return result

    def analyze_for_optimization(self, query_code: str, retrieved_context: str) -> Dict:
        prompt = self.prompt_templates.render_optimization_prompt(
            query_code=query_code,
            context=retrieved_context
        )

        result = self._call_llm(
            system_prompt=prompt['system'],
            user_prompt=prompt['user'],
            response_format="json_object"
        )

        if "error" not in result:
            opt_count = len(result.get('optimizations', []))
            speedup = result.get('estimated_speedup', 'unknown')
            print(f"Optimizations: {opt_count} | Speedup: {speedup}")

        return result

    def calculate_security_score(self, query_code: str, retrieved_context: str) -> Dict:
        prompt = self.prompt_templates.render_security_scoring_prompt(
            query_code=query_code,
            context=retrieved_context
        )

        result = self._call_llm(
            system_prompt=prompt['system'],
            user_prompt=prompt['user'],
            response_format="json_object"
        )

        if "error" not in result:
            score = result.get('overall_security_score', 0)
            severity = result.get('overall_severity', 'Unknown')
            vuln_count = len(result.get('vulnerabilities', []))
            print(f"CVSS: {score}/10 | Severity: {severity.upper()} | Vulnerabilities: {vuln_count}")

        return result

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> Dict:
        input_cost = (prompt_tokens / 1_000_000) * 2.50
        output_cost = (completion_tokens / 1_000_000) * 10.0
        total_cost = input_cost + output_cost

        return {
            'model': self.model,
            'input_tokens': prompt_tokens,
            'output_tokens': completion_tokens,
            'input_cost_usd': f"${input_cost:.6f}",
            'output_cost_usd': f"${output_cost:.6f}",
            'total_cost_usd': f"${total_cost:.6f}"
        }


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
    rag_core = RAGCore(vector_store, embedding_gen, top_k=3)
    analyzer = LLMAnalyzer(model="gpt-4o", temperature=0.3, max_tokens=2000)

    test_code = """def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    result = database.execute(query)
    return result"""

    rag_context = rag_core.build_rag_context(
        query_code=test_code,
        analysis_type="bug_detection",
        top_k=3
    )

    bug_analysis = analyzer.analyze_for_bugs(
        query_code=test_code,
        retrieved_context=rag_context['formatted_context']
    )

    output_file = "phase_2/analysis_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(bug_analysis, f, indent=2)

    print(f"Results saved to {output_file}")