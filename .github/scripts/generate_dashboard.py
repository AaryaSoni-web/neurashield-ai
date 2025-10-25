#!/usr/bin/env python3
"""
NeuraShield Security Dashboard Generator
Generates an HTML dashboard from analysis results
"""
import os
import json
from datetime import datetime


def generate_dashboard_html(results):
    """Generate HTML dashboard from analysis results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Calculate statistics
    total_files = len(results)
    total_bugs = sum(len(r.get('bug_analysis', {}).get('bugs_found', [])) for r in results)
    total_vulns = sum(len(r.get('security_analysis', {}).get('vulnerabilities', [])) for r in results)
    
    critical_files = sum(
        1 for r in results 
        if r.get('bug_analysis', {}).get('overall_risk') == 'critical'
    )
    
    high_risk_files = sum(
        1 for r in results 
        if r.get('bug_analysis', {}).get('overall_risk') == 'high'
    )
    
    avg_security_score = sum(
        r.get('security_analysis', {}).get('overall_security_score', 0) 
        for r in results
    ) / max(total_files, 1)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeuraShield Security Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .critical {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        .success {{ color: #28a745; }}
        .info {{ color: #17a2b8; }}
        
        .file-list {{
            padding: 30px;
        }}
        .file-item {{
            background: white;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .file-item.critical {{
            border-left-color: #dc3545;
        }}
        .file-item.high {{
            border-left-color: #ffc107;
        }}
        .file-name {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
            color: #333;
        }}
        .file-stats {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 10px;
        }}
        .file-stat {{
            background: #f8f9fa;
            padding: 8px 15px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ NeuraShield Security Dashboard</h1>
            <p>Generated: {timestamp}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Files Analyzed</div>
                <div class="stat-value info">{total_files}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Bugs Found</div>
                <div class="stat-value warning">{total_bugs}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Security Vulnerabilities</div>
                <div class="stat-value critical">{total_vulns}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Critical Files</div>
                <div class="stat-value critical">{critical_files}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">High Risk Files</div>
                <div class="stat-value warning">{high_risk_files}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Security Score</div>
                <div class="stat-value {'success' if avg_security_score < 3 else 'warning' if avg_security_score < 7 else 'critical'}">{avg_security_score:.1f}/10</div>
            </div>
        </div>
        
        <div class="file-list">
            <h2 style="margin-bottom: 20px;">File Analysis Details</h2>
"""
    
    # Add file details
    for result in results:
        file_path = result.get('sample_name', result.get('file_path', 'unknown'))
        bug_data = result.get('bug_analysis', {})
        sec_data = result.get('security_analysis', {})
        
        risk_level = bug_data.get('overall_risk', 'low')
        bug_count = len(bug_data.get('bugs_found', []))
        vuln_count = len(sec_data.get('vulnerabilities', []))
        security_score = sec_data.get('overall_security_score', 0)
        
        file_class = 'critical' if risk_level == 'critical' else 'high' if risk_level == 'high' else ''
        
        html += f"""
            <div class="file-item {file_class}">
                <div class="file-name">📄 {file_path}</div>
                <div class="file-stats">
                    <div class="file-stat">Risk Level: <strong>{risk_level.upper()}</strong></div>
                    <div class="file-stat">Bugs: <strong>{bug_count}</strong></div>
                    <div class="file-stat">Vulnerabilities: <strong>{vuln_count}</strong></div>
                    <div class="file-stat">Security Score: <strong>{security_score}/10</strong></div>
                </div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="footer">
            <p>Generated by NeuraShield AI - Automated Security Analysis</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    # Load analysis results
    results_file = 'phase_2/repo_analysis_results.json'
    
    if not os.path.exists(results_file):
        print(f"ERROR: {results_file} not found")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Generate dashboard
    dashboard_html = generate_dashboard_html(results)
    
    # Save dashboard
    with open('security_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("✅ Security dashboard generated: security_dashboard.html")


if __name__ == '__main__':
    main()
