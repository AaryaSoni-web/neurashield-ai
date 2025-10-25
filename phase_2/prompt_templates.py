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

# CHAIN-OF-THOUGHT ANALYSIS

Please follow these steps systematically:

**Step 1: Identify Vulnerability Types**
- Look for: SQL injection, XSS, buffer overflow, null pointer dereference, race conditions
- Check for: Input validation issues, unsafe deserialization, insecure cryptography
- Examine: Authentication/authorization flaws, information disclosure

**Step 2: Assess Exploitability**
- How difficult is it to exploit? (easy/moderate/hard)
- What prerequisites are needed?
- Can it be exploited remotely or requires local access?

**Step 3: Determine Impact (CIA Triad)**
- **Confidentiality**: Can attacker access sensitive data? (none/partial/complete)
- **Integrity**: Can attacker modify data or system behavior? (none/partial/complete)
- **Availability**: Can attacker disrupt service? (none/partial/complete)

**Step 4: Provide Specific Fix**
- Give concrete code example of the fix
- Explain why the fix works
- Suggest additional security measures

# OUTPUT FORMAT

Respond in JSON format:
{
  "has_bugs": true/false,
  "bugs_found": [
    {
      "type": "vulnerability type (e.g., SQL Injection)",
      "line": line_number or "general",
      "description": "detailed description of the bug",
      "severity": "low/medium/high/critical",
      "exploit_difficulty": "easy/moderate/hard",
      "impact": {
        "confidentiality": "none/partial/complete",
        "integrity": "none/partial/complete",
        "availability": "none/partial/complete"
      },
      "cwe_id": "CWE-XXX if applicable",
      "fix": "specific code fix with example",
      "additional_recommendations": ["list of extra security measures"]
    }
  ],
  "reasoning": "step-by-step explanation of your analysis process",
  "overall_risk": "low/medium/high/critical"
}

Be thorough and precise in your analysis.""")

    OPTIMIZATION_SYSTEM = """You are a performance optimization expert with deep knowledge of:
- Algorithm complexity analysis (Big O notation)
- Python performance best practices
- Memory efficiency and profiling
- Pythonic idioms and patterns

Use systematic reasoning to identify optimization opportunities."""

    OPTIMIZATION_TEMPLATE = Template("""Analyze the following code for optimization opportunities using Chain-of-Thought reasoning.

# CODE TO ANALYZE
{{ query_code }}

# OPTIMIZATION EXAMPLES FROM KNOWLEDGE BASE
{{ retrieved_context }}

# CHAIN-OF-THOUGHT ANALYSIS

Follow these steps:

**Step 1: Complexity Analysis**
- Calculate current time complexity (Big O)
- Calculate current space complexity (Big O)
- Identify performance bottlenecks

**Step 2: Algorithmic Improvements**
- Can we use a better algorithm?
- Are there redundant operations?
- Can we cache or memoize results?

**Step 3: Pythonic Best Practices**
- Are we using appropriate built-ins? (map, filter, comprehensions)
- Can we leverage standard library functions?
- Are there more readable/maintainable alternatives?

**Step 4: Memory Optimization**
- Are we creating unnecessary copies?
- Can we use generators instead of lists?
- Are there memory leaks or accumulation issues?

# OUTPUT FORMAT

Respond in JSON format:
{
  "current_complexity": {
    "time": "O(n) or other notation",
    "space": "O(n) or other notation",
    "bottlenecks": ["list of performance issues"]
  },
  "optimizations": [
    {
      "type": "algorithmic/syntactic/memory/library",
      "description": "what to improve",
      "current_code_snippet": "problematic code",
      "optimized_code": "improved version",
      "improvement": "expected performance gain (e.g., O(n^2) -> O(n log n))",
      "trade_offs": "any trade-offs or considerations"
    }
  ],
  "pythonic_improvements": [
    {
      "suggestion": "use list comprehension instead of for loop",
      "code_example": "optimized code"
    }
  ],
  "reasoning": "step-by-step explanation",
  "estimated_speedup": "percentage or factor (e.g., 2x faster)"
}

Prioritize readability alongside performance.""")

    SECURITY_SCORING_SYSTEM = """You are a cybersecurity expert specializing in CVSS (Common Vulnerability Scoring System) assessments. You understand:
- CVSS v3.1 scoring methodology
- NVD (National Vulnerability Database) standards
- Industry-standard severity ratings
- Risk assessment frameworks

Provide accurate CVSS scores based on industry standards."""

    SECURITY_SCORING_TEMPLATE = Template("""Assess security vulnerabilities in the code using CVSS v3.1 scoring methodology.

# CODE TO ANALYZE
{{ query_code }}

# KNOWN VULNERABILITY PATTERNS
{{ retrieved_context }}

# CVSS SCORING FRAMEWORK

Assess each vulnerability using CVSS Base Score metrics:

**Attack Vector (AV)**
- Network (N): 0.85
- Adjacent (A): 0.62
- Local (L): 0.55
- Physical (P): 0.20

**Attack Complexity (AC)**
- Low (L): 0.77
- High (H): 0.44

**Privileges Required (PR)**
- None (N): 0.85
- Low (L): 0.62
- High (H): 0.27

**User Interaction (UI)**
- None (N): 0.85
- Required (R): 0.62

**Impact (CIA)**
- None (N): 0
- Low (L): 0.22
- High (H): 0.56

# OUTPUT FORMAT

Respond in JSON format:
{
  "vulnerabilities": [
    {
      "type": "vulnerability type",
      "description": "detailed description",
      "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
      "cvss_score": 9.1,
      "severity": "Critical",
      "metrics": {
        "attack_vector": "Network",
        "attack_complexity": "Low",
        "privileges_required": "None",
        "user_interaction": "None",
        "scope": "Unchanged",
        "confidentiality_impact": "High",
        "integrity_impact": "High",
        "availability_impact": "None"
      },
      "cwe_id": "CWE-XXX",
      "remediation": "how to fix",
      "references": ["CWE links, OWASP references"]
    }
  ],
  "overall_security_score": 9.1,
  "overall_severity": "Critical",
  "risk_summary": "executive summary of security posture",
  "immediate_actions": ["prioritized list of fixes"]
}

Use precise CVSS calculations per official scoring guide.""")

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

    print(f"Prompts generated: Bug Detection ({len(bug_prompt['user'])} chars) | Optimization ({len(opt_prompt['user'])} chars) | Security ({len(sec_prompt['user'])} chars)")