import argparse
import json
import os
import sys
from pathlib import Path
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
        prompt = f"""Analyze this Python code for security vulnerabilities, best practices, and potential issues:

File: {filename}
Code:
{code_content}

Provide analysis in JSON format with:
1. "severity": "critical", "high", "medium", "low", or "none"
2. "issues": list of found issues
3. "recommendations": list of recommendations
4. "score": security score 0-100

Be specific and actionable."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Python security expert. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        analysis_text = response.choices[0].message.content
        
        # Try to parse JSON
        try:
            analysis = json.loads(analysis_text)
        except:
            # If not valid JSON, create structured response
            analysis = {
                "severity": "medium",
                "issues": [analysis_text],
                "recommendations": ["Review code manually"],
                "score": 50
            }
        
        return analysis
    
    except Exception as e:
        return {
            "severity": "unknown",
            "issues": [f"Analysis error: {str(e)}"],
            "recommendations": ["Check API key and rate limits"],
            "score": 0
        }

def scan_directory(source_path):
    """Scan directory and collect all Python files"""
    python_files = []
    total_lines = 0
    
    try:
        for root, dirs, files in os.walk(source_path):
            # Skip common directories
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
    
    return python_files, total_lines

def main():
    parser = argparse.ArgumentParser(description='NeuraShield AI Code Analysis')
    parser.add_argument('--source-path', required=True, help='Path to source code')
    parser.add_argument('--output', required=True, help='Path to output report')
    args = parser.parse_args()
    
    source_path = args.source_path
    output_path = args.output
    
    print(f"🔍 Scanning {source_path}...")
    
    # Phase 1: Scan and collect files
    python_files, total_lines = scan_directory(source_path)
    
    if not python_files:
        report = {
            "summary": "❌ No Python files found to analyze",
            "phase": "1",
            "statistics": {
                "python_files": 0,
                "total_lines": 0,
                "timestamp": str(Path(args.output).parent)
            },
            "files": [],
            "findings": []
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print("⚠️ No Python files found")
        return
    
    print(f"✅ Found {len(python_files)} Python files with {total_lines} lines")
    
    # Phase 2: Analyze each file with AI
    print("\n🤖 Phase 2: AI Analysis in progress...")
    
    files_analysis = []
    all_issues = []
    critical_count = 0
    high_count = 0
    medium_count = 0
    total_score = 0
    
    for idx, file_info in enumerate(python_files[:10], 1):  # Limit to first 10 files to save API calls
        print(f"  [{idx}/{min(len(python_files), 10)}] Analyzing {file_info['path']}...")
        
        code_content = read_file_safely(file_info['full_path'])
        analysis = analyze_code_with_ai(code_content, file_info['path'])
        
        # Track severity
        severity = analysis.get('severity', 'unknown')
        if severity == 'critical':
            critical_count += 1
        elif severity == 'high':
            high_count += 1
        elif severity == 'medium':
            medium_count += 1
        
        score = analysis.get('score', 50)
        total_score += score
        
        # Add to findings
        if analysis.get('issues'):
            for issue in analysis['issues'][:3]:  # First 3 issues
                all_issues.append({
                    "file": file_info['path'],
                    "severity": severity,
                    "issue": issue
                })
        
        files_analysis.append({
            "file": file_info['path'],
            "lines": file_info['lines'],
            "analysis": analysis
        })
    
    # Calculate average score
    avg_score = total_score // len(files_analysis) if files_analysis else 0
    
    # Generate comprehensive summary
    summary_text = f"""### 🛡️ NeuraShield AI Security Analysis Report

**📊 Statistics:**
- Total Python Files: {len(python_files)}
- Files Analyzed: {len(files_analysis)}
- Total Lines of Code: {total_lines}

**🔐 Security Score: {avg_score}/100**

**⚠️ Issues Found:**
- 🔴 Critical: {critical_count}
- 🟠 High: {high_count}
- 🟡 Medium: {medium_count}

**📋 Top Issues:**
"""
    
    for i, issue in enumerate(all_issues[:5], 1):
        summary_text += f"\n{i}. [{issue['severity'].upper()}] {issue['file']}: {issue['issue'][:80]}..."
    
    if not all_issues:
        summary_text += "\n✅ No major security issues detected!"
    
    # Build complete report
    report = {
        "summary": summary_text.strip(),
        "phase": "2",
        "timestamp": os.popen('date -Iseconds').read().strip(),
        "statistics": {
            "total_python_files": len(python_files),
            "files_analyzed": len(files_analysis),
            "total_lines": total_lines,
            "security_score": avg_score,
            "issues": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "total": len(all_issues)
            }
        },
        "files_analysis": files_analysis,
        "all_findings": all_issues,
        "recommendations": [
            "Review all critical and high severity issues immediately",
            "Implement automated code quality checks in CI/CD",
            "Consider using linters like pylint and flake8",
            "Regular security audits recommended",
            "Implement input validation and output encoding"
        ]
    }
    
    # Save report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Report saved to {output_path}")
    print(f"🔐 Security Score: {avg_score}/100")
    print(f"⚠️ Total Issues: {len(all_issues)}")

if __name__ == "__main__":
    main()
