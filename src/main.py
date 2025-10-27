import argparse
import json
import os
from datetime import datetime

try:
    import openai
except ImportError:
    os.system("pip install openai")
    import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

def read_file_safely(filepath, max_lines=50):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return ''.join(lines[:max_lines])
    except:
        return ""

def analyze_code_with_ai(code_content, filename):
    try:
        if not code_content or len(code_content.strip()) < 10:
            return {
                "severity": "low",
                "score": 85,
                "issues": [{"title": "Small file", "description": "File too small to analyze", "fix": "N/A"}]
            }
        
        prompt = f"""Analyze Python code for security.
Code: {code_content[:400]}
Return ONLY JSON: {{"severity":"high/medium/low","score":0-100,"issues":[{{"title":"str","description":"str","severity":"high/medium/low","fix":"str"}}]}}"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return only valid JSON"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        
        text = response.choices[0].message.content.strip()
        
        if text.count(chr(96)) >= 2:
            lines = text.split('\n')
            json_lines = [l for l in lines if not l.startswith(chr(96))]
            text = '\n'.join(json_lines)
        
        result = json.loads(text)
        
        if 'severity' not in result:
            result['severity'] = 'medium'
        if 'score' not in result:
            result['score'] = 65
        if 'issues' not in result:
            result['issues'] = []
        
        return result
    
    except json.JSONDecodeError:
        return {
            "severity": "medium",
            "score": 60,
            "issues": [{"title": "Parse Error", "description": "JSON parsing failed", "severity": "medium", "fix": "Review manually"}]
        }
    except Exception as e:
        return {
            "severity": "medium",
            "score": 50,
            "issues": [{"title": "API Error", "description": str(e), "severity": "high", "fix": "Check API key"}]
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
    
    html = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>NeuraShield Report</title>\n<style>\nbody { font-family: Segoe UI, Arial; background: #f5f5f5; padding: 20px; }\n.container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }\n.header { border-bottom: 3px solid #4CAF50; margin-bottom: 30px; padding-bottom: 20px; }\nh1 { color: #333; margin: 0; font-size: 32px; }\n.timestamp { color: #666; font-size: 14px; margin-top: 10px; }\n.metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }\n.metric { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; text-align: center; }\n.metric.critical { background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%); }\n.metric.high { background: linear-gradient(135deg, #ffa502 0%, #ffb84d 100%); }\n.metric.good { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }\n.metric h3 { font-size: 36px; margin: 0; font-weight: bold; }\n.metric p { font-size: 13px; margin: 8px 0 0 0; }\n.section { margin: 40px 0; }\n.section h2 { color: #333; font-size: 24px; border-bottom: 2px solid #eee; padding-bottom: 12px; margin: 0 0 20px 0; }\n.summary-list { list-style: none; padding: 0; }\n.summary-list li { padding: 8px 0; color: #555; font-size: 15px; border-bottom: 1px solid #f0f0f0; }\n.summary-list strong { color: #333; }\n.file-block { background: #f9f9f9; border-left: 5px solid #4CAF50; padding: 20px; margin: 15px 0; border-radius: 4px; }\n.file-header { font-weight: bold; font-size: 16px; color: #333; margin-bottom: 10px; }\n.file-meta { color: #666; font-size: 13px; margin-bottom: 12px; }\n.issue { background: white; border-left: 4px solid #ff6b6b; padding: 15px; margin: 12px 0; border-radius: 3px; }\n.issue.critical { border-left-color: #f5576c; }\n.issue.high { border-left-color: #ffa502; }\n.issue.medium { border-left-color: #4facfe; }\n.issue.low { border-left-color: #28a745; }\n.issue-title { font-weight: bold; color: #333; font-size: 15px; margin-bottom: 5px; }\n.issue-desc { color: #666; font-size: 13px; margin: 5px 0; line-height: 1.5; }\n.issue-fix { background: #f0f0f0; padding: 8px; margin: 8px 0; border-radius: 3px; font-size: 12px; }\n.issue-fix strong { color: #333; }\n.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-top: 8px; }\n.badge.critical { background: #f5576c; color: white; }\n.badge.high { background: #ffa502; color: white; }\n.badge.medium { background: #4facfe; color: white; }\n.badge.low { background: #28a745; color: white; }\n.rec-list { list-style: none; padding: 0; }\n.rec-item { background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 12px; margin: 10px 0; border-radius: 3px; color: #2e7d32; }\n.footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; text-align: center; }\n</style>\n</head>\n<body>\n<div class="container">\n<div class="header">\n<h1>Shield AI Security Analysis Report</h1>\n<p class="timestamp">Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' IST</p>\n</div>\n\n<div class="metrics">\n<div class="metric">\n<h3>' + str(stats.get('total_python_files', 0)) + '</h3>\n<p>Total Files</p>\n</div>\n<div class="metric critical">\n<h3>' + str(stats.get('issues', {}).get('critical', 0)) + '</h3>\n<p>Critical Issues</p>\n</div>\n<div class="metric high">\n<h3>' + str(stats.get('issues', {}).get('high', 0)) + '</h3>\n<p>High Issues</p>\n</div>\n<div class="metric good">\n<h3>' + str(score) + '%</h3>\n<p>Security Score</p>\n</div>\n</div>\n\n<div class="section">\n<h2>Analysis Summary</h2>\n<ul class="summary-list">\n<li><strong>Total Files:</strong> ' + str(stats.get('total_python_files', 0)) + '</li>\n<li><strong>Files Analyzed:</strong> ' + str(stats.get('files_analyzed', 0)) + '</li>\n<li><strong>Total Lines:</strong> ' + str(stats.get('total_lines', 0)) + '</li>\n<li><strong>Security Score:</strong> ' + str(stats.get('security_score', 0)) + '/100</li>\n<li><strong>Critical:</strong> ' + str(stats.get('issues', {}).get('critical', 0)) + '</li>\n<li><strong>High:</strong> ' + str(stats.get('issues', {}).get('high', 0)) + '</li>\n<li><strong>Medium:</strong> ' + str(stats.get('issues', {}).get('medium', 0)) + '</li>\n<li><strong>Low:</strong> ' + str(stats.get('issues', {}).get('low', 0)) + '</li>\n</ul>\n</div>\n\n<div class="section">\n<h2>File Analysis</h2>\n'
    
    for file_info in files_analysis[:15]:
        name = file_info.get('file', 'Unknown')
        analysis = file_info.get('analysis', {})
        issues = analysis.get('issues', [])
        
        html += '<div class="file-block">\n<div class="file-header">File: ' + name + '</div>\n<div class="file-meta">Lines: ' + str(file_info.get('lines', 0)) + ' | Score: ' + str(analysis.get('score', 0)) + '/100 | Severity: ' + analysis.get('severity', 'N/A').upper() + '</div>\n'
        
        if issues and len(issues) > 0:
            for issue in issues[:5]:
                sev = issue.get('severity', 'medium').lower()
                html += '<div class="issue ' + sev + '">\n<div class="issue-title">' + issue.get('title', 'Issue') + '</div>\n<div class="issue-desc">' + issue.get('description', '') + '</div>\n<div class="issue-fix"><strong>Fix:</strong> ' + issue.get('fix', 'Review') + '</div>\n<span class="badge ' + sev + '">' + sev.upper() + '</span>\n</div>\n'
        else:
            html += '<div style="color: #28a745; padding: 10px;">No issues detected</div>\n'
        
        html += '</div>\n'
    
    html += '</div>\n\n<div class="section">\n<h2>Recommendations</h2>\n<ul class="rec-list">\n'
    
    for rec in recommendations:
        html += '<li class="rec-item">' + rec + '</li>\n'
    
    html += '</ul>\n</div>\n\n<div class="footer">\n<p>NeuraShield AI Security Analysis powered by OpenAI</p>\n</div>\n</div>\n</body>\n</html>'
    
    return html

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-path', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    print("Phase 1: Scanning files...")
    python_files, total_lines = scan_directory(args.source_path)
    
    if not python_files:
        print("No Python files found")
        return
    
    print("Phase 2: AI Analysis...")
    
    files_analysis = []
    all_issues = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    total_score = 0
    
    for idx, file_info in enumerate(python_files[:10], 1):
        print(f"Analyzing {file_info['path']}...")
        
        code_content = read_file_safely(file_info['full_path'])
        analysis = analyze_code_with_ai(code_content, file_info['path'])
        
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
        "summary": "NeuraShield AI analyzed Python files",
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
            "Implement automated code quality checks in CI/CD pipeline",
            "Use security linters: bandit, pylint, flake8",
            "Setup pre-commit hooks for code analysis",
            "Regular security audits and penetration testing",
            "Implement input validation and output encoding",
            "Never hardcode secrets - use environment variables",
            "Keep dependencies updated and monitor vulnerabilities"
        ]
    }
    
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    html_path = args.output.replace('.json', '.html')
    with open(html_path, 'w') as f:
        f.write(generate_html_report(report))
    
    print("Analysis complete!")
    print(f"Score: {avg_score}/100")

if __name__ == "__main__":
    main()
