import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import openai
except ImportError:
    os.system("pip install openai")
    import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

def read_file_safely(filepath, max_lines=100):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return ''.join(lines[:max_lines])
    except:
        return ""

def analyze_code_with_ai(code_content, filename):
    try:
        prompt = f"""Analyze Python code for security issues.
File: {filename}
Code: {code_content}
Return ONLY JSON with: severity, score (0-100), issues array with title/description/fix"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Respond with only valid JSON"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        text = response.choices[0].message.content
        
        # Remove markdown wrappers
        if text.count('```
            parts = text.split('```')
            text = parts[1]
            if text.startswith('json'):
                text = text[4:]
        
        return json.loads(text)
    
    except json.JSONDecodeError:
        return {
            "severity": "medium",
            "score": 50,
            "issues": [{"title": "Analysis failed", "description": "Manual review needed", "fix": "Check code"}]
        }
    except Exception as e:
        return {
            "severity": "unknown",
            "score": 0,
            "issues": [{"title": "Error", "description": str(e), "fix": "Check API"}]
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

def generate_html_report(report_data):
    stats = report_data.get('statistics', {})
    files_analysis = report_data.get('files_analysis', [])
    recommendations = report_data.get('recommendations', [])
    
    score = stats.get('security_score', 0)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>NeuraShield Report</title>
<style>
body {{ font-family: Arial; background: #f5f5f5; padding: 20px; }}
.container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
.header {{ border-bottom: 3px solid #4CAF50; margin-bottom: 30px; }}
h1 {{ color: #333; margin: 0 0 10px 0; }}
.timestamp {{ color: #666; font-size: 12px; }}
.metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
.metric {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
.metric h3 {{ font-size: 28px; margin: 0; }}
.metric p {{ font-size: 12px; margin: 5px 0 0 0; }}
.section {{ margin: 30px 0; }}
.section h2 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
.file-block {{ background: #f9f9f9; border-left: 4px solid #4CAF50; padding: 15px; margin: 15px 0; }}
.issue {{ background: white; border-left: 4px solid #ff6b6b; padding: 10px; margin: 10px 0; }}
.issue.high {{ border-left-color: #f5576c; }}
.issue.medium {{ border-left-color: #ffa502; }}
.severity {{ display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; margin-top: 5px; }}
.severity.high {{ background: #ffa502; color: white; }}
.severity.medium {{ background: #4facfe; color: white; }}
.recommendation {{ background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 10px; margin: 8px 0; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>NeuraShield AI Security Report</h1>
<p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST</p>
</div>

<div class="metrics">
<div class="metric">
<h3>{stats.get('total_python_files', 0)}</h3>
<p>Files</p>
</div>
<div class="metric">
<h3>{stats.get('issues', {}).get('critical', 0)}</h3>
<p>Critical</p>
</div>
<div class="metric">
<h3>{stats.get('issues', {}).get('high', 0)}</h3>
<p>High</p>
</div>
<div class="metric">
<h3>{score}/100</h3>
<p>Score</p>
</div>
</div>

<div class="section">
<h2>Summary</h2>
<ul>
<li>Total Files: {stats.get('total_python_files', 0)}</li>
<li>Analyzed: {stats.get('files_analyzed', 0)}</li>
<li>Lines: {stats.get('total_lines', 0)}</li>
<li>Score: {stats.get('security_score', 0)}/100</li>
<li>Critical: {stats.get('issues', {}).get('critical', 0)}</li>
<li>High: {stats.get('issues', {}).get('high', 0)}</li>
<li>Medium: {stats.get('issues', {}).get('medium', 0)}</li>
<li>Low: {stats.get('issues', {}).get('low', 0)}</li>
</ul>
</div>

<div class="section">
<h2>File Analysis</h2>
"""
    
    for file_info in files_analysis[:10]:
        name = file_info.get('file', 'Unknown')
        analysis = file_info.get('analysis', {})
        issues = analysis.get('issues', [])
        
        html += f"""
<div class="file-block">
<strong>{name}</strong> ({file_info.get('lines', 0)} lines, Score: {analysis.get('score', 0)}/100)
"""
        
        if issues:
            for issue in issues[:3]:
                sev = issue.get('severity', 'medium').lower()
                html += f"""
<div class="issue {sev}">
<strong>{issue.get('title', 'Issue')}</strong><br>
{issue.get('description', '')}<br>
<strong>Fix:</strong> {issue.get('fix', 'N/A')}<br>
<span class="severity {sev}">{sev.upper()}</span>
</div>
"""
        else:
            html += "<p style='color: #28a745;'>✓ No issues</p>"
        
        html += "</div>"
    
    html += """
</div>

<div class="section">
<h2>Recommendations</h2>
"""
    
    for rec in recommendations:
        html += f"<div class='recommendation'>✓ {rec}</div>"
    
    html += """
</div>

<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; text-align: center;">
<p>NeuraShield AI • Powered by OpenAI</p>
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
    
    print(f"Scanning {args.source_path}...")
    python_files, total_lines = scan_directory(args.source_path)
    
    if not python_files:
        print("No Python files")
        return
    
    print(f"Found {len(python_files)} files")
    
    files_analysis = []
    all_issues = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    total_score = 0
    
    for idx, file_info in enumerate(python_files[:10], 1):
        print(f"[{idx}] Analyzing {file_info['path']}...")
        
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
        
        for issue in analysis.get('issues', [])[:3]:
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
    
    avg_score = total_score // len(files_analysis) if files_analysis else 0
    
    report = {
        "summary": f"Analyzed {len(files_analysis)} files",
        "phase": "2",
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
            "Review critical and high severity issues immediately",
            "Implement code quality checks in CI/CD",
            "Use linters: pylint, flake8, bandit",
            "Setup pre-commit hooks",
            "Regular security audits",
            "Input validation and output encoding",
            "Never hardcode secrets",
            "Keep dependencies updated"
        ]
    }
    
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    html_path = args.output.replace('.json', '.html')
    with open(html_path, 'w') as f:
        f.write(generate_html_report(report))
    
    print(f"Done! Score: {avg_score}/100")
    print(f"Reports: {args.output}, {html_path}")

if __name__ == "__main__":
    main()
