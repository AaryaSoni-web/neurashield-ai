#!/usr/bin/env python3
"""
NeuraShield PR Analyzer Script
Analyzes only changed Python files in a pull request
"""
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from phase_1.vector_store import ChromaVectorStore
from phase_1.embedding_generator import EmbeddingGenerator
from phase_2.rag_analyzer import RAGAnalyzer


def read_file_content(file_path):
    """Read content from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def analyze_changed_files(changed_files):
    """Analyze all changed Python files"""
    # Connect to existing ChromaDB
    project_root = os.path.abspath('.')
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
    
    # Analyze each changed file
    results = []
    for file_path in changed_files:
        if not file_path.endswith('.py'):
            continue
            
        print(f"\nAnalyzing: {file_path}")
        
        code = read_file_content(file_path)
        if not code:
            continue
        
        # Run full analysis (bugs, optimization, security)
        analysis = analyzer.analyze_code(code=code, analysis_type="all")
        analysis['file_path'] = file_path
        results.append(analysis)
    
    return results


def generate_markdown_report(results):
    """Generate a markdown report for PR comment"""
    lines = []
    lines.append("# 🛡️ NeuraShield Security Analysis Report")
    lines.append("")
    lines.append(f"**Analyzed Files:** {len(results)}")
    lines.append("")
    
    # Summary section
    total_bugs = sum(len(r.get('bug_analysis', {}).get('bugs_found', [])) for r in results)
    total_vulns = sum(len(r.get('security_analysis', {}).get('vulnerabilities', [])) for r in results)
    critical_issues = sum(
        1 for r in results 
        if r.get('bug_analysis', {}).get('overall_risk') == 'critical'
    )
    
    lines.append("## 📊 Summary")
    lines.append("")
    lines.append(f"- 🐛 **Total Bugs:** {total_bugs}")
    lines.append(f"- 🔒 **Security Vulnerabilities:** {total_vulns}")
    lines.append(f"- 🔴 **Critical Issues:** {critical_issues}")
    lines.append("")
    
    # Detailed file-by-file analysis
    lines.append("---")
    lines.append("")
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        lines.append(f"## 📄 `{file_path}`")
        lines.append("")
        
        # Bug Analysis
        bug_data = result.get('bug_analysis', {})
        if bug_data.get('has_bugs', False):
            bugs = bug_data.get('bugs_found', [])
            risk = bug_data.get('overall_risk', 'unknown').upper()
            
            lines.append(f"### 🐛 Bugs Found: {len(bugs)} (Risk: {risk})")
            lines.append("")
            
            for i, bug in enumerate(bugs, 1):
                lines.append(f"**{i}. {bug['type']}** (Severity: `{bug['severity']}`)")
                lines.append(f"- **Line:** {bug.get('line', 'N/A')}")
                lines.append(f"- **Description:** {bug['description']}")
                lines.append(f"- **Fix:** {bug.get('fix', 'No fix provided')[:200]}")
                if 'cwe_id' in bug:
                    lines.append(f"- **CWE:** {bug['cwe_id']}")
                lines.append("")
        else:
            lines.append("### ✅ No Bugs Detected")
            lines.append("")
        
        # Security Analysis
        sec_data = result.get('security_analysis', {})
        if sec_data and not sec_data.get('error'):
            score = sec_data.get('overall_security_score', 0)
            severity = sec_data.get('overall_severity', 'Unknown').upper()
            
            lines.append(f"### 🔒 Security Score: {score}/10 (Severity: {severity})")
            lines.append("")
            
            vulns = sec_data.get('vulnerabilities', [])
            if vulns:
                for i, vuln in enumerate(vulns, 1):
                    lines.append(f"**{i}. {vuln['type']}**")
                    lines.append(f"- **CVSS Score:** {vuln.get('cvss_score', 'N/A')}")
                    lines.append(f"- **CWE:** {vuln.get('cwe_id', 'N/A')}")
                    lines.append(f"- **Remediation:** {vuln.get('remediation', 'N/A')[:150]}")
                    lines.append("")
        
        # Optimization Suggestions
        opt_data = result.get('optimization_analysis', {})
        if opt_data and not opt_data.get('error'):
            optimizations = opt_data.get('optimizations', [])
            if optimizations:
                lines.append(f"### ⚡ Optimizations Available: {len(optimizations)}")
                lines.append("")
                speedup = opt_data.get('estimated_speedup', 'N/A')
                lines.append(f"**Estimated Speedup:** {speedup}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    lines.append("*Generated by NeuraShield AI*")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python pr_analyzer.py <file1.py> <file2.py> ...")
        sys.exit(1)
    
    # Get list of changed files from command line arguments
    changed_files = sys.argv[1:]
    
    print(f"Analyzing {len(changed_files)} changed files...")
    
    # Run analysis
    results = analyze_changed_files(changed_files)
    
    if not results:
        print("No files to analyze")
        sys.exit(0)
    
    # Save results as JSON
    with open('pr_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Generate markdown report for PR comment
    markdown_report = generate_markdown_report(results)
    with open('pr_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print("\n✅ Analysis complete!")
    print(f"Results saved to: pr_analysis_results.json")
    print(f"Report saved to: pr_analysis_report.md")


if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    main()
