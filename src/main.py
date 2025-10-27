import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import openai
except ImportError:
    print("⚠️ OpenAI not installed. Installing...")
    os.system("pip install openai")
    import openai

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def read_file_safely(filepath, max_lines=100):
    """Read file safely with line limit"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return ''.join(lines[:max_lines])
    except Exception as e:
        return f"Error reading file: {str(e)}"

def analyze_code_with_ai(code_content, filename):
    """Use OpenAI to analyze code for security issues"""
    try:
        prompt = f"""Analyze this Python code for security vulnerabilities and best practices:

File: {filename}
Code:
{code_content}

Provide analysis in JSON format with these fields:
- severity: critical, high, medium, low, or none
- score: 0-100 security score
- issues: list of {{title, description, severity, fix}}
- strengths: list of good practices
- recommendations: list of recommendations

Return ONLY valid JSON, no markdown."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Python security expert. Respond with ONLY valid JSON, no markdown wrappers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        analysis_text = response.choices[0].message.content.strip()
        
        # Clean up any markdown wrappers
        if analysis_text.startswith('```
            # Remove markdown code blocks
            lines = analysis_text.split('\n')
            analysis_text = '\n'.join(```')])
        
        analysis = json.loads(analysis_text)
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {str(e)}")
        analysis = {
            "severity": "medium",
            "score": 50,
            "issues": [{"title": "Manual Review Required", "description": "Could not parse AI response", "severity": "medium", "fix": "Review manually"}],
            "strengths": [],
            "recommendations": ["Review code manually"]
        }
    
    except Exception as e:
        print(f"Analysis Error: {str(e)}")
        analysis = {
            "severity": "unknown",
            "score": 0,
            "issues": [{"title": "Analysis Error", "description": str(e), "severity": "medium", "fix": "Check API key"}],
            "strengths": [],
            "recommendations": ["Check OpenAI API key and rate limits"]
        }
    
    return analysis

def scan_directory(source_path):
    """Scan directory and collect Python files"""
    python_files = []
    total_lines = 0
    
    try:
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, source_path)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            total_lines += lines
                            python_files.append({
                                'path': rel_path,
                                'full_path': filepath,
                                'lines': lines
                            })
                    except:
                        pass
    
    except Exception as e:
        print(f"Error scanning directory: {str(e)}")
    
    return sorted(python_files, key=lambda x: x['lines'], reverse=True), total_lines

def generate_html_report(report_data):
    """Generate HTML version of the report"""
    files_analysis = report_data.get('files_analysis', [])
    stats = report_data.get('statistics', {})
    recommendations = report_data.get('recommendations', [])
    
    score = stats.get('security_score', 0)
    score_class = 'danger' if score < 40 else 'warning' if score < 70 else ''
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeuraShield AI Security Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 40px; }}
        .header {{ border-bottom: 3px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #333; margin-bottom: 10px; }}
        .header .timestamp {{ color: #666; font-size: 14px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric.high {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric.medium {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric.low {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        .metric h3 {{ font-size: 28px; margin-bottom: 5px; }}
        .metric p {{ font-size: 12px; opacity: 0.9; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #eee; }}
        .file-analysis {{ background: #f9f9f9; border-left: 4px solid #4CAF50; padding: 15px; margin-bottom: 15px; border-radius: 4px; }}
        .file-analysis .filename {{ font-weight: bold; color: #333; margin-bottom: 10px; }}
        .issue {{ background: white; border-left: 4px solid #ff6b6b; padding: 10px; margin: 10px 0; border-radius: 4px; }}
        .issue.high {{ border-left-color: #f5576c; }}
        .issue.medium {{ border-left-color: #ffa502; }}
        .issue.low {{ border-left-color: #28a745; }}
        .issue .title {{ font-weight: bold; color: #333; }}
        .issue .severity {{ display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 12px; margin-top: 5px; font-weight: bold; }}
        .severity.critical {{ background: #f5576c; color: white; }}
        .severity.high {{ background: #ffa502; color: white; }}
        .severity.medium {{ background: #4facfe; color: white; }}
        .severity.low {{ background: #43e97b; color: #333; }}
        .recommendation {{ background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 10px; margin: 8px 0; border-radius: 4px; }}
        .score-badge {{ display: inline-block; background: #4CAF50; color: white; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 18px; }}
        .score-badge.danger {{ background: #f5576c; }}
        .score-badge.warning {{ background: #ffa502; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; text-align: center; }}
        ul {{ margin-left: 20px; color: #666; line-height: 1.8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ NeuraShield AI Security Analysis Report</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <h3>{stats.get('total_python_files', 0)}</h3>
                <p>Python Files</p>
            </div>
            <div class="metric high">
                <h3>{stats.get('issues', {}).get('critical', 0)}</h3>
                <p>Critical Issues</p>
            </div>
            <div class="metric medium">
                <h3>{stats.get('issues', {}).get('high', 0)}</h3>
                <p>High Issues</p>
            </div>
            <div class="metric low">
                <h3><span class="score-badge {score_class}">{score}</span></h3>
                <p>Security Score</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Analysis Summary</h2>
            <ul>
                <li>Total Python Files: <strong>{stats.get('total_python_files', 0)}</strong></li>
                <li>Files Analyzed: <strong>{stats.get('files_analyzed', 0)}</strong></li>
                <li>Total Lines of Code: <strong>{stats.get('total_lines', 0)}</strong></li>
                <li>Security Score: <strong>{stats.get('security_score', 0)}/100</strong></li>
                <li>Critical Issues: <strong>{stats.get('issues', {}).get('critical', 0)}</strong></li>
                <li>High Issues: <strong>{stats.get('issues', {}).get('high', 0)}</strong></li>
                <li>Medium Issues: <strong>{stats.get('issues', {}).get('medium', 0)}</strong></li>
                <li>Low Issues: <strong>{stats.get('issues', {}).get('low', 0)}</strong></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📁 File Analysis Details</h2>
"""
    
    for file_info in files_analysis[:10]:
        filename = file_info.get('file', 'Unknown')
        analysis = file_info.get('analysis', {})
        issues = analysis.get('issues', [])
        
        html += f"""
            <div class="file-analysis">
                <div class="filename">📄 {filename}</div>
                <div style="margin: 10px 0; color: #666; font-size: 14px;">
                    Lines: {file_info.get('lines', 0)} | 
                    Security Score: <strong>{analysis.get('score', 'N/A')}/100</strong> |
                    Severity: <strong>{analysis.get('severity', 'N/A').upper()}</strong>
                </div>
"""
        
        if issues:
            for issue in issues[:5]:
                severity = issue.get('severity', 'medium').lower()
                title = issue.get('title', 'Issue')
                desc = issue.get('description', '')
                fix = issue.get('fix', '')
                
                html += f"""
                <div class="issue {severity}">
                    <div class="title">⚠️ {title}</div>
                    <div style="color: #666; margin: 5px 0; font-size: 13px;">{desc}</div>
                    <div style="color: #666; margin: 5px 0; font-size: 13px; background: #f0f0f0; padding: 8px; border-radius: 3px;">
                        <strong>✓ Fix:</strong> {fix}
                    </div>
                    <span class="severity {severity}">{severity.upper()}</span>
                </div>
"""
        else:
            html += '<div style="color: #28a745; padding: 10px; margin: 10px 0; background: #f0f8f5; border-radius: 3px;">✅ No issues detected</div>'
        
        html += '</div>'
    
    html += """
        </div>
        
        <div class="section">
            <h2>📋 Recommendations</h2>
"""
    
    for rec in recommendations[:8]:
        html += f'<div class="recommendation">✓ {rec}</div>'
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>NeuraShield AI Security Analysis • Powered by OpenAI GPT-3.5 • {datetime.now().strftime('%Y-%m-%d')}</p>
            <p><a href="https://github.com/AaryaSoni-web/neurashield-ai" style="color: #4CAF50; text-decoration: none;">View on GitHub →</a></p>
        </div>
    </div>
</body>
</html>
"""
    return html

def main():
    parser = argparse.ArgumentParser(description='NeuraShield AI Code Analysis')
    parser.add_argument('--source-path', required=True, help='Path to source code')
    parser.add_argument('--output', required=True, help='Path to output report')
    args = parser.parse_args()
    
    source_path = args.source_path
    output_path = args.output
    
    print(f"🔍 Scanning {source_path}...")
    
    # Phase 1: Scan files
    python_files, total_lines = scan_directory(source_path)
    
    if not python_files:
        print("❌ No Python files found")
        report = {
            "summary": "No Python files found",
            "phase": "1",
            "statistics": {"total_python_files": 0, "files_analyzed": 0, "total_lines": 0, "security_score": 0},
            "files_analysis": [],
            "all_findings": [],
            "recommendations": []
        }
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        return
    
    print(f"✅ Found {len(python_files)} Python files with {total_lines} lines")
    
    # Phase 2: AI Analysis
    print("\n🤖 Phase 2: AI Analysis in progress...")
    
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
        
        # Track counts
        severity = analysis.get('severity', 'unknown').lower()
        if severity == 'critical':
            critical_count += 1
        elif severity == 'high':
            high_count += 1
        elif severity == 'medium':
            medium_count += 1
        else:
            low_count += 1
        
        score = analysis.get('score', 50)
        total_score += score
        
        # Collect issues
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
    
    # Build report
    report = {
        "summary": f"NeuraShield AI analyzed {len(files_analysis)} Python files and found {len(all_issues)} total issues.",
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
            "Review all critical and high severity issues immediately",
            "Implement automated code quality checks in CI/CD pipeline",
            "Use linters: pylint, flake8, bandit for security checks",
            "Set up pre-commit hooks for code analysis",
            "Regular security audits and penetration testing",
            "Implement input validation and output encoding",
            "Use environment variables for sensitive data, never hardcode secrets",
            "Keep dependencies updated and use tools like Dependabot"
        ]
    }
    
    # Generate HTML report
    html_content = generate_html_report(report)
    
    # Save JSON
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save HTML
    html_path = output_path.replace('.json', '.html')
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 JSON Report: {output_path}")
    print(f"🌐 HTML Report: {html_path}")
    print(f"🔐 Security Score: {avg_score}/100")
    print(f"⚠️ Total Issues: {len(all_issues)}")

if __name__ == "__main__":
    main()
