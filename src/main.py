#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path (neurashield-ai root)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Add phase directories to path
phase1_dir = os.path.join(parent_dir, 'phase_1')
phase2_dir = os.path.join(parent_dir, 'phase_2')
sys.path.insert(0, phase1_dir)
sys.path.insert(0, phase2_dir)

try:
    from phase_1.vector_store import ChromaVectorStore
    from phase_1.embedding_generator import EmbeddingGenerator
    from phase_2.rag_analyzer import RAGAnalyzer
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)


def analyze_repository(source_path, max_files=None):
    """Analyze repository using actual NeuraShield pipeline"""
    
    print("\n" + "="*70)
    print("PHASE 1: BUILDING VECTOR STORE")
    print("="*70)
    
    # Use parent directory for db_path (neurashield-ai root)
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, 'phase_1', 'chroma_db')
    
    # Ensure directory exists
    os.makedirs(db_path, exist_ok=True)
    
    try:
        # Initialize vector store
        vector_store = ChromaVectorStore(
            collection_name="neurashield_code_v1",
            persist_directory=db_path
        )
        
        embedding_gen = EmbeddingGenerator()
        
        print("✓ Vector store initialized")
        print("✓ Embedding generator ready")
    except Exception as e:
        print(f"ERROR: Failed to initialize vector store: {e}")
        sys.exit(1)
    
    # Initialize RAG analyzer for Phase 2
    print("\n" + "="*70)
    print("PHASE 2: ANALYZING CODE")
    print("="*70)
    
    try:
        analyzer = RAGAnalyzer(
            vector_store=vector_store,
            embedding_generator=embedding_gen,
            llm_model="gpt-3.5-turbo",
            top_k=5
        )
    except Exception as e:
        print(f"ERROR: Failed to initialize RAG analyzer: {e}")
        sys.exit(1)
    
    # Scan and analyze files
    python_files = []
    total_lines = 0
    
    # Walk through source directory
    for root, dirs, files in os.walk(source_path):
        # Exclude common non-code directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules', '.github']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        python_files.append({
                            'path': os.path.relpath(filepath, source_path),
                            'full_path': filepath,
                            'lines': lines
                        })
                except Exception as e:
                    print(f"Warning: Could not read {filepath}: {e}")
                    pass
    
    print(f"Found {len(python_files)} Python files with {total_lines} lines")
    
    # Determine how many files to analyze
    if max_files is None:
        files_to_analyze = python_files
    else:
        files_to_analyze = python_files[:max_files]
    
    print(f"Analyzing {len(files_to_analyze)} files...")
    
    files_analysis = []
    all_findings = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    total_score = 0
    
    for idx, file_info in enumerate(files_to_analyze, 1):
        print(f"[{idx}/{len(files_to_analyze)}] Analyzing {file_info['path']}...")
        
        try:
            with open(file_info['full_path'], 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()
            
            # Skip empty files
            if not code_content.strip():
                print(f"  Skipping empty file")
                continue
            
            # Run full analysis
            analysis = analyzer.analyze_code(code=code_content, analysis_type="all")
            
            # Extract findings
            bugs = analysis.get('bug_analysis', {}).get('bugs_found', [])
            vulnerabilities = analysis.get('security_analysis', {}).get('vulnerabilities', [])
            
            for bug in bugs:
                severity = bug.get('severity', 'medium').lower()
                if severity == 'critical':
                    critical_count += 1
                elif severity == 'high':
                    high_count += 1
                elif severity == 'medium':
                    medium_count += 1
                
                all_findings.append({
                    'file': file_info['path'],
                    'type': 'bug',
                    'title': bug.get('type', 'Bug'),
                    'severity': severity,
                    'description': bug.get('description', ''),
                    'fix': bug.get('fix', ''),
                    'cwe': bug.get('cwe_id', '')
                })
            
            for vuln in vulnerabilities:
                cvss_score = vuln.get('cvss_score', 0)
                if isinstance(cvss_score, str):
                    try:
                        cvss_score = float(cvss_score)
                    except:
                        cvss_score = 0
                
                sev = 'high' if cvss_score >= 7 else 'medium'
                if cvss_score >= 9:
                    sev = 'critical'
                
                all_findings.append({
                    'file': file_info['path'],
                    'type': 'vulnerability',
                    'title': vuln.get('type', 'Vulnerability'),
                    'severity': sev,
                    'description': vuln.get('description', ''),
                    'cvss_score': cvss_score,
                    'cwe': vuln.get('cwe_id', '')
                })
            
            # Calculate score
            score = analysis.get('security_analysis', {}).get('overall_security_score', 50)
            if isinstance(score, str):
                score = int(score) if score.isdigit() else 50
            
            total_score += score
            
            files_analysis.append({
                'file': file_info['path'],
                'lines': file_info['lines'],
                'analysis': analysis
            })
        
        except Exception as e:
            print(f"  Error analyzing {file_info['path']}: {e}")
            continue
    
    avg_score = int(total_score / len(files_analysis)) if files_analysis else 0
    
    return {
        'summary': f"NeuraShield AI analyzed {len(files_analysis)} Python files and generated comprehensive security report",
        'timestamp': datetime.now().isoformat(),
        'statistics': {
            'total_python_files': len(python_files),
            'files_analyzed': len(files_analysis),
            'total_lines': total_lines,
            'security_score': avg_score,
            'issues': {
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'total': len(all_findings)
            }
        },
        'files_analysis': files_analysis,
        'all_findings': all_findings,
        'recommendations': [
            'Review all critical and high severity issues immediately',
            'Implement automated code quality checks in CI/CD pipeline',
            'Use security linters: bandit, pylint, flake8',
            'Setup pre-commit hooks for code analysis',
            'Regular security audits and penetration testing',
            'Implement input validation and output encoding',
            'Never hardcode secrets - use environment variables',
            'Keep dependencies updated and monitor vulnerabilities'
        ]
    }


def generate_text_report(report_data):
    """Generate detailed text report"""
    stats = report_data['statistics']
    findings = report_data['all_findings']
    recommendations = report_data['recommendations']
    
    text = "\n" + "="*70 + "\n"
    text += "NEURASHIELD.AI - CODE ANALYSIS REPORT\n"
    text += "="*70 + "\n"
    text += f"Timestamp: {report_data['timestamp']}\n"
    text += f"Files Analyzed: {stats['files_analyzed']}/{stats['total_python_files']}\n"
    text += f"Total Lines: {stats['total_lines']}\n"
    text += "\n" + "-"*70 + "\n\n"
    
    # BUG DETECTION
    bugs = [f for f in findings if f['type'] == 'bug']
    text += "## BUG DETECTION\n"
    text += "-"*70 + "\n"
    text += f"BUGS FOUND: {len(bugs)}\n"
    text += f"Overall Risk: {'CRITICAL' if stats['issues']['critical'] > 0 else 'HIGH' if stats['issues']['high'] > 0 else 'MEDIUM' if stats['issues']['medium'] > 0 else 'LOW'}\n\n"
    
    for idx, bug in enumerate(bugs[:10], 1):
        text += f"{idx}. {bug['title']}\n"
        text += f"   File: {bug['file']}\n"
        text += f"   Severity: {bug['severity'].upper()}\n"
        text += f"   Description: {bug['description']}\n"
        if bug.get('fix'):
            text += f"   Fix: {bug['fix']}\n"
        if bug.get('cwe'):
            text += f"   CWE: {bug['cwe']}\n"
        text += "\n"
    
    # SECURITY SCORING
    avg_cvss = stats['security_score'] * 0.1
    text += "\n## SECURITY SCORING (CVSS v3.1)\n"
    text += "-"*70 + "\n"
    text += f"Overall Security Score: {avg_cvss:.1f}/10\n"
    text += f"Severity: {'CRITICAL' if avg_cvss >= 9 else 'HIGH' if avg_cvss >= 7 else 'MEDIUM'}\n\n"
    
    vulns = [f for f in findings if f['type'] == 'vulnerability']
    text += f"VULNERABILITIES: {len(vulns)}\n\n"
    
    for idx, vuln in enumerate(vulns[:10], 1):
        text += f"{idx}. {vuln['title']}\n"
        text += f"   File: {vuln['file']}\n"
        text += f"   CVSS Score: {vuln.get('cvss_score', 'N/A')}\n"
        text += f"   Severity: {vuln['severity'].upper()}\n"
        if vuln.get('cwe'):
            text += f"   CWE: {vuln['cwe']}\n"
        text += "\n"
    
    # RECOMMENDATIONS
    text += "\n## RECOMMENDATIONS\n"
    text += "-"*70 + "\n"
    for rec in recommendations:
        text += f"• {rec}\n"
    
    text += "\nImmediate Actions Required:\n"
    if stats['issues']['critical'] > 0:
        text += "  • Fix all critical issues immediately\n"
    if stats['issues']['high'] > 0:
        text += "  • Address high severity findings\n"
    text += "  • Conduct code review\n"
    text += "  • Update dependencies\n"
    
    text += "\n" + "="*70 + "\n"
    text += "END OF REPORT\n"
    text += "="*70 + "\n"
    
    return text


def main():
    parser = argparse.ArgumentParser(description='NeuraShield AI Code Analysis')
    parser.add_argument('--source-path', required=True, help='Path to source code')
    parser.add_argument('--output', required=True, help='Path to output report')
    parser.add_argument('--max-files', type=int, default=None, help='Maximum number of files to analyze (default: all)')
    args = parser.parse_args()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    if not os.path.exists(args.source_path):
        print(f"ERROR: Source path does not exist: {args.source_path}")
        sys.exit(1)
    
    print("\nNeuraShield AI - Code Analysis Tool")
    print("="*70)
    print(f"Source: {args.source_path}")
    print(f"Output: {args.output}")
    
    # Run analysis
    try:
        report = analyze_repository(args.source_path, max_files=args.max_files)
    except Exception as e:
        print(f"\nERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*70)
    print("GENERATING REPORTS")
    print("="*70)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Save JSON report
    try:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✓ JSON Report: {args.output}")
    except Exception as e:
        print(f"ERROR: Failed to save JSON report: {e}")
        sys.exit(1)
    
    # Save text report
    try:
        text_path = args.output.replace('.json', '.txt')
        with open(text_path, 'w') as f:
            f.write(generate_text_report(report))
        print(f"✓ Text Report: {text_path}")
    except Exception as e:
        print(f"WARNING: Failed to save text report: {e}")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"Security Score: {report['statistics']['security_score']}/100")
    print(f"Critical Issues: {report['statistics']['issues']['critical']}")
    print(f"High Issues: {report['statistics']['issues']['high']}")
    print(f"Total Findings: {report['statistics']['issues']['total']}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
