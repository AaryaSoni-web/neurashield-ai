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
        
        prompt = f"""Analyze this Python code for security issues and return ONLY JSON.

Code:
{code_content[:500]}

JSON format (no markdown):
{{"severity": "critical/high/medium/low", "score": 0-100, "issues": [{{"title": "string", "description": "string", "severity": "high/medium/low", "fix": "string"}}]}}"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a security expert. Return only valid JSON, no markdown or explanation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Remove markdown if present
        if response_text.startswith('```
            lines = response_text.split('\n')
            json_lines = ```')]
            response_text = '\n'.join(json_lines)
        
        # Parse JSON
        result = json.loads(response_text)
        
        # Ensure all required fields
        if 'severity' not in result:
            result['severity'] = 'medium'
        if 'score' not in result:
            result['score'] = 65
        if 'issues' not in result:
            result['issues'] = []
        
        return result
    
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        return {
            "severity": "medium",
            "score": 60,
            "issues": [{"title": "Analysis Error", "description": f"Failed to parse response: {str(e)}", "severity": "medium", "fix": "Review manually"}]
        }
    except Exception as e:
        print(f"API error: {str(e)}")
        return {
            "severity": "medium",
            "score": 50,
            "issues": [{"title": "API Error", "description": str(e), "severity": "high", "fix": "Check OpenAI API key"}]
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
    
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>NeuraShield Security Report</title>
<style>
body { font-family: Segoe UI, Arial; background: #f5f5f5; padding: 20px; }
.container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.header { border-bottom: 3px solid #4CAF50; margin-bottom: 30px; padding-bottom: 20px; }
h1 { color: #333; margin: 0; font-size: 32px; }
.timestamp { color: #666; font-size: 14px; margin-top: 10px; }
.metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }
.metric { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.metric.critical { background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%); }
.metric.high { background: linear-gradient(135deg, #ffa502 0%, #ffb84d 100%); }
.metric.good { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.metric h3 { font-size: 36px; margin: 0; font-weight: bold; }
.metric p { font-size: 13px; margin: 8px 0 0 0; opacity: 0.95; }
.section { margin: 40px 0; }
.section h2 { color: #333; font-size: 24px; border-bottom: 2px solid #eee; padding-bottom: 12px; margin: 0 0 20px 0; }
.summary-list { list-style: none; padding: 0; }
.summary-list li { padding: 8px 0; color: #555; font-size: 15px; border-bottom: 1px solid #f0f0f0; }
.summary-list strong { color: #333; }
.file-block { background: #f9f9f9; border-left: 5px solid #4CAF50; padding: 20px; margin: 15px 0; border-radius: 4px; }
.file-header { font-weight: bold; font-size: 16px; color: #333; margin-bottom: 10px; }
.file-meta { color: #666; font-size: 13px; margin-bottom: 12px; }
.issue { background: white; border-left: 4px solid #ff6b6b; padding: 15px; margin: 12px 0; border-radius: 3px; }
.issue.critical { border-left-color: #f5576c; }
.issue.high { border-left-color: #ffa502; }
.issue.medium { border-left-color: #4facfe; }
.issue.low { border-left-color: #28a745; }
.issue-title { font-weight: bold; color: #333; font-size: 15px; margin-bottom: 5px; }
.issue-desc { color: #666; font-size: 13px; margin: 5px 0; line-height: 1.5; }
.issue-fix { background: #f0f0f0; padding: 8px; margin: 8px 0; border-radius: 3px; font-size: 12px; }
.issue-fix strong { color: #333; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-top: 8px; }
.badge.critical { background: #f5576c; color: white; }
.badge.high { background: #ffa502; color: white; }
.badge.medium { background: #4facfe; color: white; }
.badge.low { background: #28a745; color: white; }
.rec-list { list-style: none; padding: 0; }
.rec-item { background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 12px; margin: 10px 0; border-radius: 3px; color: #2e7d32; }
.footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; text-align: center; }
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🛡️ NeuraShield AI Security Analysis Report</h1>
<p class="timestamp">Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """ IST</p>
</div>

<div class="metrics">
<div class="metric">
<h3>""" + str(stats.get('total_python_files', 0)) + """</h3>
<p>Total Files</p>
</div>
<div class="metric critical">
<h3>""" + str(stats.get('issues', {}).get('critical', 0)) + """</h3>
<p>Critical Issues</p>
</div>
<div class="metric high">
<h3>""" + str(stats.get('issues', {}).get('high', 0)) + """</h3>
<p>High Issues</p>
</div>
<div class="metric good">
<h3>""" + str(score) + """%</h3>
<p>Security Score</p>
</div>
</div>

<div class="section">
<h2>📊 Analysis Summary</h2>
<ul class="summary-list">
<li><strong>Total Python Files:</strong> """ + str(stats.get('total_python_files', 0)) + """</li>
<li><strong>Files Analyzed:</strong> """ + str(stats.get('files_analyzed', 0)) + """</li>
<li><strong>Total Lines of Code:</strong> """ + str(stats.get('total_lines', 0)) + """</li>
<li><strong>Security Score:</strong> """ + str(stats.get('security_score', 0)) + """/100</li>
<li><strong>Critical Issues:</strong> """ + str(stats.get('issues', {}).get('critical', 0)) + """</li>
<li><strong>High Issues:</strong> """ + str(stats.get('issues', {}).get('high', 0)) + """</li>
<li><strong>Medium Issues:</strong> """ + str(stats.get('issues', {}).get('medium', 0)) + """</li>
<li><strong>Low Issues:</strong> """ + str(stats.get('issues', {}).get('low', 0)) + """</li>
</ul>
</div>

<div class="section">
<h2>📁 File Analysis Details</h2>
"""
    
    for file_info in files_analysis[:15]:
        name = file_info.get('file', 'Unknown')
        analysis = file_info.get('analysis', {})
        issues = analysis.get('issues', [])
        
        html += '<div class="file-block">\n'
        html += '<div class="file-header">📄 ' + name + '</div>\n'
        html += '<div class="file-meta">Lines: ' + str(file_info.get('lines', 0)) + ' | Security Score: ' + str(analysis.get('score', 0)) + '/100 | Severity: ' + analysis.get('severity', 'N/A').upper() + '</div>\n'
        
        if issues and len(issues) > 0:
            for issue in issues[:5]:
                sev = issue.get('severity', 'medium').lower()
                html += '<div class="issue ' + sev + '">\n'
                html += '<div class="issue-title">' + issue.get('title', 'Issue') + '</div>\n'
                html += '<div class="issue-desc">' + issue.get('description', '') + '</div>\n'
                html += '<div class="issue-fix"><strong>Fix:</strong> ' + issue.get('fix', 'Review manually') + '</div>\n'
                html += '<span class="badge ' + sev + '">' + sev.upper() + '</span>\n'
                html += '</div>\n'
        else:
            html += '<div style="color: #28a745; padding: 10px; background: #f0f8f5; border-radius: 3px;">✅ No security issues detected</div>\n'
        
        html += '</div>\n'
    
    html += """</div>

<div class="section">
<h2>📋 Recommendations</h2>
<ul class="rec-list">
"""
    
    for rec in recommendations:
        html += '<li class="rec-item">✓ ' + rec + '</li>\n'
    
    html += """</ul>
</div>

<div class="footer">
<p><strong>NeuraShield AI Security Analysis</strong> • Powered by OpenAI GPT-3.5 Turbo</p>
<p>Report generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """ IST</p>
<p><a href="https://github.com/AaryaSoni-web/neurashield-ai" style="color: #4CAF50; text-decoration: none;">View on GitHub →</a></p>
</div>
</div>
</body>
</html>
"""
    return html

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-path', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    print(f"🔍 Phase 1: Scanning {args.source_path}...")
    python_files, total_lines = scan_directory(args.source_path)
    
    if not python_files:
        print("❌ No Python files found")
        return
    
    print(f"✅ Found {len(python_files)} Python files with {total_lines} lines")
    
    print(f"\n🤖 Phase 2: AI Analysis starting...")
    
    files_analysis = []
    all_issues = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    total_score = 0
    
    for idx, file_info in enumerate(python_files[:10], 1):
        print(f"  [{idx}/{min(len(python_files), 10)}] Analyzing {file_info['path']}...")
        
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
            "Implement automated code quality checks in CI/CD pipeline",
            "Use security linters: bandit, pylint, flake8",
            "Setup pre-commit hooks for code analysis",
            "Conduct regular security audits and penetration testing",
            "Implement comprehensive input validation and output encoding",
            "Never hardcode secrets - use environment variables and secure vaults",
            "Keep all dependencies updated and monitor for vulnerabilities with Dependabot"
        ]
    }
    
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    html_path = args.output.replace('.json', '.html')
    with open(html_path, 'w') as f:
        f.write(generate_html_report(report))
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 JSON Report: {args.output}")
    print(f"🌐 HTML Report: {html_path}")
    print(f"🔐 Security Score: {avg_score}/100")
    print(f"⚠️ Total Issues Found: {len(all_issues)}")

if __name__ == "__main__":
    main()
