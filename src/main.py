import argparse
import json
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='NeuraShield AI Code Analysis')
    parser.add_argument('--source-path', required=True, help='Path to source code to analyze')
    parser.add_argument('--output', required=True, help='Path to output report JSON file')
    args = parser.parse_args()
    
    # Analyze the source code
    source_path = args.source_path
    
    # Count Python files and lines
    py_files = 0
    total_lines = 0
    findings = []
    
    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith('.py'):
                py_files += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        
                        # Check for common issues
                        with open(filepath, 'r') as f2:
                            content = f2.read()
                            if 'exec(' in content:
                                findings.append(f"⚠️ Found dangerous 'exec()' in {file}")
                            if 'eval(' in content:
                                findings.append(f"⚠️ Found dangerous 'eval()' in {file}")
                            if 'pickle' in content and 'loads(' in content:
                                findings.append(f"⚠️ Found unsafe pickle deserialization in {file}")
                except:
                    pass
    
    # Generate report
    report = {
        "summary": f"✅ Analyzed {py_files} Python files with {total_lines} lines of code. Found {len(findings)} potential security issues.",
        "statistics": {
            "python_files": py_files,
            "total_lines": total_lines,
            "files_analyzed": py_files
        },
        "findings": findings if findings else ["✅ No major security issues detected"]
    }
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Analysis complete. Report saved to {args.output}")
    print(f"📊 Files: {py_files} | Lines: {total_lines} | Issues: {len(findings)}")

if __name__ == "__main__":
    main()
