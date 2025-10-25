#!/usr/bin/env python3
import sys, subprocess, os


def get_staged_files():
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
        files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py') and f]
        
        # Exclude scanner itself and test files
        excluded = ['.githooks/pre_commit_scan.py', '.github/scripts/', 'tests/']
        filtered = []
        for f in files:
            skip = False
            for exc in excluded:
                if exc in f:
                    skip = True
                    break
            if not skip:
                filtered.append(f)
        return filtered
    except:
        return []


def check_file(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except:
        return []
    
    issues = []
    
    for i, line in enumerate(lines, 1):
        # Skip comments and strings that are just patterns
        if line.strip().startswith('#'):
            continue
        if '# nosec' in line or '# skipcq' in line:
            continue
        
        # Check 1: Hardcoded secrets (password, api_key assignments)
        line_lower = line.lower()
        if ('password' in line_lower or 'api_key' in line_lower or 'secret' in line_lower):
            if '=' in line and ('"' in line or "'" in line):
                if 'if ' not in line and 'in ' not in line and 'or ' not in line:
                    issues.append((i, 'CRITICAL', 'Hardcoded Secret'))
        
        # Check 2: SQL Injection
        if 'execute(' in line and '+' in line and ('select' in line_lower or 'where' in line_lower):
            if 'if ' not in line and 'SELECT' not in line.upper():
                issues.append((i, 'HIGH', 'SQL Injection'))
        
        # Check 3: Code Injection
        if ('eval(' in line or 'exec(') in line:
            if 'if ' not in line and 'in line' not in line:
                issues.append((i, 'HIGH', 'Code Injection'))
    
    return issues


print("\n🛡️  NeuraShield Scanner\n")

files = get_staged_files()

if not files:
    print("✅ No Python files to scan\n")
    sys.exit(0)

all_issues = []

for f in files:
    issues = check_file(f)
    if issues:
        print(f"📄 {f}")
        for line_no, severity, issue_type in issues:
            emoji = '🔴' if severity == 'CRITICAL' else '🟠'
            print(f"  {emoji} Line {line_no}: {issue_type} [{severity}]")
            all_issues.append((severity, f, line_no))

critical = sum(1 for s, _, _ in all_issues if s == 'CRITICAL')
high = sum(1 for s, _, _ in all_issues if s == 'HIGH')

print(f"📊 Total: {len(all_issues)} issues | Critical: {critical} | High: {high}\n")

if critical > 0:
    print("❌ BLOCKED: Critical issues found!\n")
    sys.exit(1)

print("✅ Commit allowed\n")
sys.exit(0)
