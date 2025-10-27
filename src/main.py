import argparse
import json
import os
import re
from datetime import datetime

def read_file_safely(filepath, max_lines=100):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return ''.join(lines[:max_lines])
    except:
        return ""

def analyze_code_locally(code_content, filename):
    """Local code analysis without OpenAI"""
    issues = []
    severity = "low"
    score = 85
    
    if not code_content or len(code_content.strip()) < 10:
        return {
            "severity": "low",
            "score": 85,
            "issues": [{"title": "Small file", "description": "File too small to analyze", "fix": "N/A"}]
        }
    
    lines = code_content.split('\n')
    
    # Check for security issues
    for line_num, line in enumerate(lines, 1):
        # SQL Injection
        if 'execute' in line and ('f"' in line or "f'" in line or '%' in line):
            issues.append({
                "title": "Potential SQL Injection",
                "description": f"Line {line_num}: Dynamic SQL query detected",
                "severity": "high",
                "fix": "Use parameterized queries instead of string formatting"
            })
            severity = "high"
            score = max(score - 20, 0)
        
        # Hardcoded credentials
        if re.search(r'(password|secret|api_key|token)\s*=\s*["\']', line, re.IGNORECASE):
            issues.append({
                "title": "Hardcoded Credentials",
                "description": f"Line {line_num}: Potential hardcoded secret found",
                "severity": "critical",
                "fix": "Use environment variables or secure vaults"
            })
            severity = "critical"
            score = max(score - 30, 0)
        
        # Unsafe eval
        if 'eval(' in line or 'exec(' in line:
            issues.append({
                "title": "Unsafe eval/exec",
                "description": f"Line {line_num}: eval() or exec() detected",
                "severity": "critical",
                "fix": "Avoid eval/exec, use safer alternatives"
            })
            severity = "critical"
            score = max(score - 25, 0)
        
        # Pickle deserialization
        if 'pickle.load' in line or 'pickle.loads' in line:
            issues.append({
                "title": "Unsafe Pickle Deserialization",
                "description": f"Line {line_num}: Pickle deserialization detected",
                "severity": "high",
                "fix": "Use JSON or other safe serialization formats"
            })
            severity = "high"
            score = max(score - 15, 0)
        
        # No input validation
        if 'input(' in line and 'str(' not in line:
            issues.append({
                "title": "Missing Input Validation",
                "description": f"Line {line_num}: User input without validation",
                "severity": "medium",
                "fix": "Always validate and sanitize user input"
            })
            score = max(score - 5, 0)
        
        # Weak randomness
        if 'random.' in line and 'secrets.' not in line:
            issues.append({
                "title": "Weak Random Number Generation",
                "description": f"Line {line_num}: Using random module for security",
                "severity": "medium",
                "fix": "Use secrets module for cryptographic operations"
            })
            score = max(score - 10, 0)
    
    # Check for good practices
    if 'try:' in code_content and 'except' in code_content:
        score = min(score + 5, 100)
    
    if 'logging' in code_content:
        score = min(score + 3, 100)
    
    if 'assert' in code_content:
        score = min(score + 2, 100)
    
    # Limit issues to top 5
    issues = sorted(issues, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x['severity'], 4))[:5]
    
    if not issues:
        issues = [{"title": "Code Review Passed", "description": "No major security issues detected", "severity": "low", "fix": "N/A"}]
    
    return {
        "severity": severity,
        "score": max(score, 0),
        "issues": issues
    }

def scan_directory(source_path):
    python_files = []
    total_lines = 0
    
    for root, dirs, files in os.walk(source_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
        
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

def generate_html_report(report_data):
    stats = report_data.get('statistics', {})
    files_analysis = report_data.get('files_analysis', [])
    recommendations = report_data.get('recommendations', [])
    score = stats.get('security_score', 0)
    
    html = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>NeuraShield Report</title>\n<style>\nbody { font-family: Segoe UI, Arial; background: #f5f5f5; padding: 20px; }\n.container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }\n.header { border-bottom: 3px solid #4CAF50; margin-bottom: 30px; padding-bottom: 20px; }\nh1 { color: #333; margin: 0; font-size: 32px; }\n.timestamp { color: #666; font-size: 14px; margin-top: 10px; }\n.metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }\n.metric { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; text-align: center; }\n.metric.critical { background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%); }\n.metric.high { background: linear-gradient(135deg, #ffa502 0%, #ffb84d 100%); }\n.metric.good { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }\n.metric h3 { font-size: 36px; margin: 0; font-weight: bold; }\n.metric p { font-size: 13px; margin: 8px 0 0 0; }\n.section { margin: 40px 0; }\n.section h2 { color: #333; font-size: 24px; border-bottom: 2px solid #eee; padding-bottom: 12px; margin: 0 0 20px 0; }\n.summary-list { list-style: none; padding: 0; }\n.summary-list li { padding: 8px 0; color: #555; font-size: 15px; border-bottom: 1px solid #f0f0f0; }\n.summary-list strong { color: #333; }\n.file-block { background: #f9f9f9; border-left: 5px solid #4CAF50; padding: 20px; margin: 15px 0; border-radius: 4px; }\n.file-header { font-weight: bold; font-size: 16px; color: #333; margin-bottom: 10px; }\n.file-meta { color: #666; font-size: 13px; margin-bottom: 12px; }\n.issue { background: white; border-left: 4px solid #ff6b6b; padding: 15px; margin: 12px 0; border-radius: 3px; }\n.issue.critical { border-left-color: #f5576c; }\n.issue.high { border-left-color: #ffa502; }\n.issue.medium { border-left-color: #4facfe; }\n.issue.low { border-left-color: #28a745; }\n.issue-title { font-weight: bold; color: #333; font-size: 15px; margin-bottom: 5px; }\n.issue-desc { color: #666; font-size: 13px; margin: 5px 0; line-height: 1.5; }\n.issue-fix { background: #f0f0f0; padding: 8px; margin: 8px 0; border-radius: 3px; font-size: 12px; }\n.issue-fix strong { color: #333; }\n.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-top: 8px; }\n.badge.critical { background: #f5576c; color: white; }\n.badge.high { background: #ffa502; color: white; }\n.badge.medium { background: #4facfe; color: white; }\n.badge.low { background: #28a745; color: white; }\n.rec-list { list-style: none; padding: 0; }\n.rec-item { background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 12px; margin: 10px 0; border-radius: 3px; color: #2e7d32; }\n.footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; text-align: center; }\n</style>\n</head>\n<body>\n<div class="container">\n<div class="header">\n<h1>NeuraShield AI Security Analysis Report</h1>\n<p class="timestamp">Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' IST</p>\n</div>\n\n<div class="metrics">\n<div class="metric">\n<h3>' + str(stats.get('total_python_files', 0)) + '</h3>\n<p>Total Files</p>\n</div>\n<div class="metric critical">\n<h3>' + str(stats.get('issues', {}).get('critical', 0)) + '</h3>\n<p>Critical Issues</p>\n</div>\n<div class="metric high">\n<h3>' + str(stats.get('issues', {}).get('high', 0)) + '</h3>\n<p>High Issues</p>\n</div>\n<div class="metric good">\n<h3>' + str(score) + '</h3>\n<p>Security Score</p>\n</div>\n</div>\n\n<div class="section">\n<h2>Analysis Summary</h2>\n<ul class="summary-list">\n<li><strong>Total Files:</strong> ' + str(stats.get('total_python_files', 0)) + '</li>\n<li><strong>Files Analyzed:</strong> ' + str(stats.get('files_analyzed', 0)) + '</li>\n<li><strong>Total Lines:</strong> ' + str(stats.get('total_lines', 0)) + '</li>\n<li><strong>Security Score:</strong> ' + str(stats.get('security_score', 0)) + '/100</li>\n<li><strong>Critical Issues:</strong> ' + str(stats.get('issues', {}).get('critical', 0)) + '</li>\n<li><strong>High Issues:</strong> ' + str(stats.get('issues', {}).get('high', 0)) + '</li>\n<li><strong>Medium Issues:</strong> ' + str(stats.get('issues', {}).get('medium', 0)) + '</li>\n<li><strong>Low Issues:</strong> ' + str(stats.get('issues', {}).get('low', 0)) + '</li>\n</ul>\n</div>\n\n<div class="section">\n<h2>File Analysis Details</h2>\n'
    
    for file_info in files_analysis[:20]:
        name = file_info.get('file', 'Unknown')
        analysis = file_info.get('analysis', {})
        issues = analysis.get('issues', [])
        
        html += '<div class="file-block">\n<div class="file-header">File: ' + name + '</div>\n<div class="file-meta">Lines: ' + str(file_info.get('lines', 0)) + ' | Score: ' + str(analysis.get('score', 0)) + '/100 | Severity: ' + analysis.get('severity', 'N/A').upper() + '</div>\n'
        
        if issues and len(issues) > 0:
            for issue in issues[:5]:
                sev = issue.get('severity', 'medium').lower()
                html += '<div class="issue ' + sev + '">\n<div class="issue-title">' + issue.get('title', 'Issue') + '</div>\n<div class="issue-desc">' + issue.get('description', '') + '</div>\n<div class="issue-fix"><strong>Fix:</strong> ' + issue.get('fix', 'Review') + '</div>\n<span class="badge ' + sev + '">' + sev.upper() + '</span>\n</div>\n'
        else:
            html += '<div style="color: #28a745; padding: 10px; background: #f0f8f5;">No security issues detected</div>\n'
        
        html += '</div>\n'
    
    html += '</div>\n\n<div class="section">\n<h2>Recommendations</h2>\n<ul class="rec-list">\n'
    
    for rec in recommendations:
        html += '<li class="rec-item">✓ ' + rec + '</li>\n'
    
    html += '</ul>\n</div>\n\n<div class="footer">\n<p>NeuraShield AI Security Analysis • Local Code Analysis</p>\n<p>Report generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' IST</p>\n</div>\n</div>\n</body>\n</html>'
    
    return html

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-path', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("PHASE 1: SCANNING FILES")
    print("="*50)
    python_files, total_lines = scan_directory(args.source_path)
    
    if not python_files:
        print("No Python files found")
        return
    
    print(f"Found {len(python_files)} Python files")
    print(f"Total lines of code: {total_lines}")
    
    print("\n" + "="*50)
    print("PHASE 2: ANALYZING CODE")
    print("="*50)
    
    files_analysis = []
    all_issues = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    total_score = 0
    
    for idx, file_info in enumerate(python_files[:20], 1):
        print(f"[{idx}/{min(len(python_files), 20)}] Analyzing: {file_info['path']}")
        
        code_content = read_file_safely(file_info['full_path'])
        analysis = analyze_code_locally(code_content, file_info['path'])
        
        sev = analysis.get('severity', 'unknown').lower()
        if sev == 'critical':
            critical_count += 1
        elif sev == 'high':
            high_count += 1
        elif sev == 'medium':
            medium_count += 1
        else:
            low_count += 1
        
        score = analysis.get('score', 50)
        total_score += score
        
        for issue in analysis.get('issues', [])[:5]:
            all_issues.append({
                "file": file_info['path'],
                "severity": issue.get('severity', 'medium'),
                "title": issue.get('title', 'Issue'),
                "description": issue.get('description', ''),
                "fix": issue.get('fix', '')
            })
        
        files_analysis.append({
            "file": file_info['path'],
            "lines": file_info['lines'],
            "analysis": analysis
        })
    
    avg_score = int(total_score / len(files_analysis)) if files_analysis else 0
    
    report = {
        "summary": f"NeuraShield AI analyzed {len(files_analysis)} Python files and generated comprehensive security report",
        "phase": "2_complete",
        "timestamp": datetime.now().isoformat(),
        "statistics": {
            "total_python_files": len(python_files),
            "files_analyzed": len(files_analysis),
            "total_lines": total_lines,
            "security_score": avg_score,
            "issues": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
                "total": len(all_issues)
            }
        },
        "files_analysis": files_analysis,
        "all_findings": all_issues,
        "recommendations": [
            "Review all critical and high severity issues immediately",
            "Implement input validation for all user inputs",
            "Use parameterized queries to prevent SQL injection",
            "Store secrets in environment variables, never hardcode",
            "Avoid eval() and exec() - use safer alternatives",
            "Use secrets module for cryptographic randomness",
            "Implement proper error handling and logging",
            "Keep dependencies updated and monitor vulnerabilities"
        ]
    }
    
    print("\n" + "="*50)
    print("GENERATING REPORTS")
    print("="*50)
    
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✓ JSON report saved: {args.output}")
    
    html_path = args.output.replace('.json', '.html')
    with open(html_path, 'w') as f:
        f.write(generate_html_report(report))
    print(f"✓ HTML report saved: {html_path}")
    
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE")
    print("="*50)
    print(f"Security Score: {avg_score}/100")
    print(f"Critical Issues: {critical_count}")
    print(f"High Issues: {high_count}")
    print(f"Medium Issues: {medium_count}")
    print(f"Low Issues: {low_count}")
    print(f"Total Issues Found: {len(all_issues)}")
    print("="*50)

if __name__ == "__main__":
    main()
