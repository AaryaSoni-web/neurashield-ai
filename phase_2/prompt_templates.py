import os
import sys
from typing import Dict
from jinja2 import Template

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase_2.rag_core import RAGCore
from phase_1.embedding_generator import EmbeddingGenerator
from phase_1.vector_store import ChromaVectorStore


class PromptTemplates:
    
    BUG_DETECTION_SYSTEM = """You are an expert software security analyst specializing in vulnerability detection and bug identification. You have deep knowledge of:
- OWASP Top 10 vulnerabilities
- Common coding mistakes and anti-patterns
- Security best practices
- Exploitability assessment

Use systematic Chain-of-Thought reasoning to analyze code thoroughly."""

    BUG_DETECTION_TEMPLATE = Template("""Analyze the following code for potential bugs and vulnerabilities using a step-by-step Chain-of-Thought approach.

# CODE TO ANALYZE
{{ query_code }}

# SIMILAR BUG PATTERNS FROM KNOWLEDGE BASE
{{ retrieved_context }}

# OUTPUT FORMAT
Respond ONLY with valid JSON (no markdown, no extra text):

{
  "has_bugs": true/false,
  "bugs_found": [
    {
      "type": "vulnerability type",
      "line": "line number or general",
      "description": "detailed description",
      "severity": "low/medium/high",
      "cwe_id": "CWE-XXX"
    }
  ],
  "overall_risk": "low/medium/high"
}""")

    OPTIMIZATION_SYSTEM = """You are a performance optimization expert with deep knowledge of:
- Algorithm complexity analysis (Big O notation)
- Python performance best practices
- Memory efficiency and profiling
- Pythonic idioms and patterns

Use systematic reasoning to identify optimization opportunities."""

    OPTIMIZATION_TEMPLATE = Template("""Analyze the following code for optimization opportunities.

# CODE TO ANALYZE
{{ query_code }}

# OPTIMIZATION EXAMPLES FROM KNOWLEDGE BASE
{{ retrieved_context }}

# OUTPUT FORMAT
Respond ONLY with valid JSON (no markdown, no extra text):

{
  "current_complexity": {
    "time": "O(n) or other notation",
    "space": "O(n) or other notation",
    "bottlenecks": ["list of issues"]
  },
  "optimizations": [
    {
      "type": "algorithmic/syntactic",
      "description": "what to improve",
      "improvement": "expected gain"
    }
  ],
  "estimated_speedup": "2x or percentage"
}""")

    SECURITY_SCORING_SYSTEM = """You are a cybersecurity expert specializing in CVSS assessments."""

    SECURITY_SCORING_TEMPLATE = Template("""Assess security vulnerabilities in this code.

# CODE TO ANALYZE
{{ query_code }}

# KNOWN VULNERABILITY PATTERNS
{{ retrieved_context }}

# OUTPUT FORMAT
Respond ONLY with valid JSON (no markdown, no extra text):

{
  "overall_security_score": 7.5,
  "overall_severity": "HIGH",
  "vulnerabilities": [
    {
      "type": "vulnerability type",
      "cvss_score": 7.5,
      "severity": "HIGH",
      "description": "detailed description",
      "remediation": "how to fix"
    }
  ],
  "risk_summary": "executive summary",
  "immediate_actions": ["list of fixes"]
}""")

    @classmethod
    def render_bug_detection_prompt(cls, query_code: str, context: str) -> Dict:
        return {
            'system': cls.BUG_DETECTION_SYSTEM,
            'user': cls.BUG_DETECTION_TEMPLATE.render(
                query_code=query_code,
                retrieved_context=context
            )
        }

    @classmethod
    def render_optimization_prompt(cls, query_code: str, context: str) -> Dict:
        return {
            'system': cls.OPTIMIZATION_SYSTEM,
            'user': cls.OPTIMIZATION_TEMPLATE.render(
                query_code=query_code,
                retrieved_context=context
            )
        }

    @classmethod
    def render_security_scoring_prompt(cls, query_code: str, context: str) -> Dict:
        return {
            'system': cls.SECURITY_SCORING_SYSTEM,
            'user': cls.SECURITY_SCORING_TEMPLATE.render(
                query_code=query_code,
                retrieved_context=context
            )
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

    test_code = """def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)"""

    rag_context = rag_core.build_rag_context(
        query_code=test_code,
        analysis_type="bug_detection",
        top_k=3
    )

    templates = PromptTemplates()
    bug_prompt = templates.render_bug_detection_prompt(test_code, rag_context['formatted_context'])
    opt_prompt = templates.render_optimization_prompt(test_code, rag_context['formatted_context'])
    sec_prompt = templates.render_security_scoring_prompt(test_code, rag_context['formatted_context'])

    print(f"Prompts generated successfully")