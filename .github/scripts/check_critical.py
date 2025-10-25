#!/usr/bin/env python3
"""
NeuraShield Critical Issue Checker
Checks analysis results for critical issues and blocks PR if found
"""
import sys
import json


def check_for_critical_issues(results_file):
    """Check if there are any critical security issues"""
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {results_file} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in {results_file}")
        sys.exit(1)
    
    critical_issues = []
    high_severity_bugs = []
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        
        # Check bug analysis for critical risk
        bug_data = result.get('bug_analysis', {})
        if bug_data.get('overall_risk') == 'critical':
            critical_issues.append({
                'file': file_path,
                'type': 'Critical Bug Risk',
                'details': bug_data.get('bugs_found', [])
            })
        
        # Check for high/critical severity bugs
        bugs = bug_data.get('bugs_found', [])
        for bug in bugs:
            if bug.get('severity') in ['high', 'critical']:
                high_severity_bugs.append({
                    'file': file_path,
                    'bug': bug
                })
        
        # Check security analysis for critical vulnerabilities
        sec_data = result.get('security_analysis', {})
        if sec_data.get('overall_severity') in ['CRITICAL', 'Critical']:
            critical_issues.append({
                'file': file_path,
                'type': 'Critical Security Vulnerability',
                'score': sec_data.get('overall_security_score', 0)
            })
    
    # Report findings
    if critical_issues or high_severity_bugs:
        print("\n" + "="*70)
        print("🔴 CRITICAL ISSUES DETECTED - PR CANNOT BE MERGED")
        print("="*70)
        
        if critical_issues:
            print(f"\n❌ {len(critical_issues)} Critical Issue(s):")
            for issue in critical_issues:
                print(f"  - {issue['file']}: {issue['type']}")
        
        if high_severity_bugs:
            print(f"\n❌ {len(high_severity_bugs)} High/Critical Severity Bug(s):")
            for item in high_severity_bugs:
                bug = item['bug']
                print(f"  - {item['file']}: {bug['type']} (Line {bug.get('line', 'N/A')})")
                print(f"    {bug['description']}")
        
        print("\n" + "="*70)
        print("Please fix these critical issues before merging.")
        print("="*70 + "\n")
        
        sys.exit(1)  # Exit with error code to block PR
    else:
        print("\n✅ No critical issues found. PR can be merged.")
        sys.exit(0)


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_critical.py <results.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    check_for_critical_issues(results_file)


if __name__ == '__main__':
    main()
