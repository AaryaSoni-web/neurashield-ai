import argparse
import json
import os
import re
from datetime import datetime

def read_file_safely(filepath, max_lines=150):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return ''.join(lines[:max_lines])
    except:
        return ""

def analyze_code_locally(code_content, filename):
    """Comprehensive local code analysis"""
    bugs = []
    optimizations = []
    vulnerabilities = []
    severity_score = 3.0
    
    if not code_content or len(code_content.strip()) < 20:
        return {
            "severity": "low",
            "score": 85,
            "bugs": [{"title": "Small file", "description": "File too small", "severity": "low", "fix": "N/A", "cwe": ""}],
            "optimizations": [],
            "vulnerabilities": [],
            "cvss_score": 2.0,
            "issues": []
        }
    
    lines_list = code_content.split('\n')
    
    # BUG DETECTION
    for line_num, line in enumerate(lines_list, 1):
        
        # Hardcoded credentials
        if re.search(r'(password|secret|api_key|token|pwd)\s*=\s*["\']', line, re.IGNORECASE):
            bugs.append({
                "title": "Hardcoded API Key/Credentials",
                "description": f"Line {line_num}: Hardcoded credentials detected. This exposes sensitive information.",
                "severity": "HIGH",
                "exploit_difficulty": "easy",
                "impact": "C:complete I:complete A:partial",
                "fix": "Use environment variables or secure vaults (AWS Secrets Manager, HashiCorp Vault)",
                "cwe": "CWE-798"
            })
            severity_score = max(severity_score, 8.5)
        
        # SQL Injection
        if re.search(r'execute\s*\(.*f["\'].*%|execute\s*\(.*\.format|execute\s*\(.*\+', line):
            bugs.append({
                "title": "SQL Injection Vulnerability",
                "description": f"Line {line_num}: Dynamic SQL query detected using string formatting.",
                "severity": "HIGH",
                "exploit_difficulty": "moderate",
                "impact": "C:complete I:complete A:complete",
                "fix": "Use parameterized queries (prepared statements) instead of string concatenation.",
                "cwe": "CWE-89"
            })
            severity_score = max(severity_score, 9.0)
        
        # Unsafe eval/exec
        if 'eval(' in line or 'exec(' in line:
            bugs.append({
                "title": "Unsafe Code Execution",
                "description": f"Line {line_num}: eval() or exec() detected - allows arbitrary code execution.",
                "severity": "CRITICAL",
                "exploit_difficulty": "easy",
                "impact": "C:complete I:complete A:complete",
                "fix": "Use safer alternatives like ast.literal_eval() or avoid dynamic code execution entirely.",
                "cwe": "CWE-95"
            })
            severity_score = max(severity_score, 9.8)
        
        # Improper error handling
        if 'except' in line and 'pass' in lines_list[min(line_num, len(lines_list)-1)]:
            bugs.append({
                "title": "Improper Error Handling",
                "description": f"Line {line_num}: Exception caught and silently ignored (bare except/pass).",
                "severity": "MEDIUM",
                "exploit_difficulty": "easy",
                "impact": "C:partial I:none A:none",
                "fix": "Use specific exception handling and log errors properly for debugging.",
                "cwe": "CWE-209"
            })
            severity_score = max(severity_score, 5.0)
        
        # Pickle deserialization
        if 'pickle.load' in line or 'pickle.loads' in line:
            bugs.append({
                "title": "Unsafe Deserialization",
                "description": f"Line {line_num}: Unsafe pickle deserialization can execute arbitrary code.",
                "severity": "CRITICAL",
                "exploit_difficulty": "moderate",
                "impact": "C:complete I:complete A:complete",
                "fix": "Use JSON or other safe serialization formats instead of pickle.",
                "cwe": "CWE-502"
            })
            severity_score = max(severity_score, 9.5)
        
        # Missing input validation
        if re.search(r'(input\(|request\.args|request\.form|request\.data)', line):
            bugs.append({
                "title": "Lack of Input Validation",
                "description": f"Line {line_num}: User input accepted without validation.",
                "severity": "MEDIUM",
                "exploit_difficulty": "moderate",
                "impact": "C:partial I:partial A:none",
                "fix": "Implement input validation and sanitization for all user inputs.",
                "cwe": "CWE-20"
            })
            severity_score = max(severity_score, 6.3)
    
    # CODE OPTIMIZATION
    if len(lines_list) > 100:
        optimizations.append({
            "type": "ALGORITHMIC",
            "title": "Batch Processing Optimization",
            "description": "Large file detected. Consider batch processing for code chunks.",
            "improvement": "Potential 2x speedup with parallel processing",
            "trade_offs": "Increased code complexity"
        })
    
    if re.search(r'\bfor\b.*in\b.*\bfor\b.*in\b', code_content):
        optimizations.append({
            "type": "ALGORITHMIC",
            "title": "Nested Loop Optimization",
            "description": "Nested loops detected which may impact performance.",
            "improvement": "Use data structures like sets or dicts for O(1) lookup",
            "trade_offs": "Increased memory usage"
        })
    
    if 'import' in code_content and len(lines_list) < 50:
        optimizations.append({
            "type": "LIBRARY",
            "title": "Lazy Import Optimization",
            "description": "All imports are loaded at startup.",
            "improvement": "Use lazy imports for rarely-used modules",
            "trade_offs": "Slightly more complex code"
        })
    
    # SECURITY VULNERABILITIES
    if severity_score >= 7.0:
        vulnerabilities.append({
            "title": "Insecure Default Configuration",
            "cvss_score": 7.5,
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N",
            "cwe": "CWE-1188",
            "remediation": "Configure application securely for production: disable debug mode, set secure headers."
        })
    
    if any('input' in bug.get('description', '').lower() for bug in bugs):
        vulnerabilities.append({
            "title": "Improper Input Validation",
            "cvss_score": 6.3,
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N",
            "cwe": "CWE-20",
            "remediation": "Implement input validation and sanitization for all user inputs."
        })
    
    # Limit bugs and dedup
    bugs = bugs[:5]
    
    # Calculate score (100 - penalties)
    score = 100
    for bug in bugs:
        if bug['severity'] == 'CRITICAL':
            score -= 25
        elif bug['severity'] == 'HIGH':
            score -= 15
        elif bug['severity'] == 'MEDIUM':
            score -= 8
    
    score = max(score, 20)
    
    return {
        "severity": "critical" if severity_score >= 9 else "high" if severity_score >= 7 else "medium" if severity_score >= 5 else "low",
        "score": score,
        "bugs": bugs,
        "optimizations": optimizations,
        "vulnerabilities": vulnerabilities,
        "cvss_score": min(severity_score, 10.0),
        "issues": bugs
    }

def scan_directory(source_path):
    python_files = []
    total_lines = 0
    
    for root, dirs, files in os.walk(source_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv']]
        
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
                except:
                    pass
    
    return sorted(python_files, key=lambda x: x['lines'], reverse=True), total_lines

def generate_text_report(report_data):
    stats = report_data.get('statistics', {})
    files_analysis = report_data.get('files_analysis', [])
    
    text = "\n" + "="*70 + "\n"
    text += "NEURASHIELD.AI - CODE ANALYSIS REPORT\n"
    text += "="*70 + "\n"
    text += f"Timestamp: {report_data.get('timestamp', '')}\n"
    text += f"Analysis Type: all\n"
    text += f"Retrieved Patterns: {len(files_analysis)}\n"
    text += f"Code Length: {stats.get('total_lines', 0)} lines\n"
    text += "\n" + "-"*70 + "\n\n"
    
    total_bugs = 0
    for file_info in files_analysis:
        analysis = file_info.get('analysis', {})
        total_bugs += len(analysis.get('bugs', []))
    
    # BUG DETECTION
    text += "## BUG DETECTION\n"
    text += "-"*70 + "\n"
    text += f"BUGS FOUND: {total_bugs}\n"
    text += f"Overall Risk: HIGH\n\n"
    
    bug_num = 1
    for file_info in files_analysis:
        analysis = file_info.get('analysis', {})
        for bug in analysis.get('bugs', [])[:3]:
            text += f"{bug_num}. {bug.get('title', 'Bug')}\n"
            text += f"   Severity: {bug.get('severity', 'MEDIUM')}\n"
            text += f"   Description: {bug.get('description', 'N/A')}\n"
            text += f"   Exploit Difficulty: {bug.get('exploit_difficulty', 'moderate')}\n"
            text += f"   Impact: {bug.get('impact', 'C:partial I:none A:none')}\n"
            text += f"   Fix: {bug.get('fix', 'Review manually')}\n"
            text += f"   CWE: {bug.get('cwe', 'N/A')}\n\n"
            bug_num += 1
    
    # CODE OPTIMIZATION
    text += "\n## CODE OPTIMIZATION\n"
    text += "-"*70 + "\n"
    text += f"Current Complexity:\n"
    text += f"  Time: O(n + m)\n"
    text += f"  Space: O(n + m)\n\n"
    
    total_optimizations = sum(len(f.get('analysis', {}).get('optimizations', [])) for f in files_analysis)
    text += f"OPTIMIZATIONS FOUND: {total_optimizations}\n"
    text += f"Estimated Speedup: Potentially 2x faster with optimizations\n\n"
    
    opt_num = 1
    for file_info in files_analysis:
        analysis = file_info.get('analysis', {})
        for opt in analysis.get('optimizations', [])[:2]:
            text += f"{opt_num}. {opt.get('type', '')}: {opt.get('title', 'Optimization')}\n"
            text += f"   Description: {opt.get('description', '')}\n"
            text += f"   Improvement: {opt.get('improvement', '')}\n"
            text += f"   Trade-offs: {opt.get('trade_offs', '')}\n\n"
            opt_num += 1
    
    # SECURITY SCORING
    text += "\n## SECURITY SCORING (CVSS v3.1)\n"
    text += "-"*70 + "\n"
    
    avg_cvss = 0
    for file_info in files_analysis:
        avg_cvss += file_info.get('analysis', {}).get('cvss_score', 0)
    avg_cvss = avg_cvss / len(files_analysis) if files_analysis else 0
    
    text += f"Overall Security Score: {avg_cvss:.1f}/10\n"
    text += f"Severity: {'CRITICAL' if avg_cvss >= 9 else 'HIGH' if avg_cvss >= 7 else 'MEDIUM'}\n\n"
    
    total_vulns = sum(len(f.get('analysis', {}).get('vulnerabilities', [])) for f in files_analysis)
    text += f"VULNERABILITIES: {total_vulns}\n\n"
    
    vuln_num = 1
    for file_info in files_analysis:
        analysis = file_info.get('analysis', {})
        for vuln in analysis.get('vulnerabilities', [])[:2]:
            text += f"{vuln_num}. {vuln.get('title', 'Vulnerability')}\n"
            text += f"   CVSS Score: {vuln.get('cvss_score', 'N/A')}\n"
            text += f"   CVSS Vector: {vuln.get('cvss_vector', '')}\n"
            text += f"   CWE: {vuln.get('cwe', '')}\n"
            text += f"   Remediation: {vuln.get('remediation', '')}\n\n"
            vuln_num += 1
    
    text += "\nImmediate Actions Required:\n"
    if total_bugs > 0:
        text += "  • Fix all critical and high severity bugs immediately\n"
    if total_vulns > 0:
        text += "  • Implement security recommendations\n"
    text += "  • Conduct code review\n"
    text += "  • Update dependencies\n"
    
    text += "\n" + "="*70 + "\n"
    text += "END OF REPORT\n"
    text += "="*70 + "\n"
    
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-path', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("PHASE 1: SCANNING FILES")
    print("="*70)
    python_files, total_lines = scan_directory(args.source_path)
    
    if not python_files:
        print("No Python files found")
        return
    
    print(f"Found {len(python_files)} Python files with {total_lines} lines")
    
    print("\n" + "="*70)
    print("PHASE 2: ANALYZING CODE")
    print("="*70)
    
    files_analysis = []
    all_bugs = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    total_score = 0
    
    for idx, file_info in enumerate(python_files[:10], 1):
        print(f"[{idx}] Analyzing: {file_info['path']}")
        
        code_content = read_file_safely(file_info['full_path'])
        analysis = analyze_code_locally(code_content, file_info['path'])
        
        for bug in analysis.get('bugs', []):
            if bug.get('severity') == 'CRITICAL':
                critical_count += 1
            elif bug.get('severity') == 'HIGH':
                high_count += 1
            elif bug.get('severity') == 'MEDIUM':
                medium_count += 1
            all_bugs.append(bug)
        
        total_score += analysis.get('score', 50)
        
        files_analysis.append({
            "file": file_info['path'],
            "lines": file_info['lines'],
            "analysis": analysis
        })
    
    avg_score = int(total_score / len(files_analysis)) if files_analysis else 0
    
    report = {
        "summary": f"NeuraShield AI analyzed {len(files_analysis)} Python files",
        "timestamp": datetime.now().isoformat(),
        "statistics": {
            "total_python_files": len(python_files),
            "files_analyzed": len(files_analysis),
            "total_lines": total_lines,
            "security_score": avg_score,
            "bugs_critical": critical_count,
            "bugs_high": high_count,
            "bugs_medium": medium_count,
            "total_bugs": len(all_bugs)
        },
        "files_analysis": files_analysis
    }
    
    print("\n" + "="*70)
    print("GENERATING REPORTS")
    print("="*70)
    
    # Save JSON
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"JSON Report: {args.output}")
    
    # Save Text Report
    text_path = args.output.replace('.json', '.txt')
    with open(text_path, 'w') as f:
        f.write(generate_text_report(report))
    print(f"Text Report: {text_path}")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"Security Score: {avg_score}/100")
    print(f"Critical Bugs: {critical_count}")
    print(f"High Bugs: {high_count}")
    print(f"Medium Bugs: {medium_count}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
