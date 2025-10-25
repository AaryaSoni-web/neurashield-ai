#!/usr/bin/env python3
"""
NeuraShield Pre-Commit Scanner - Simple & Fast Version
Only scans changed Python files for critical vulnerabilities
"""

import os
import sys
import json
from typing import List, Dict

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

try:
    from phase_1.embedding_generator import EmbeddingGenerator
    from phase_1.vector_store import ChromaVectorStore
    from phase_2.rag_analyzer import RAGAnalyzer
except ImportError as e:
    print(f"⚠️  Error importing modules: {e}")
    print("⚠️  Skipping NeuraShield scan")
    sys.exit(0)


def scan_files(files: List[str]) -> Dict:
    """Scan files and return analysis results"""
    
    # Initialize NeuraShield components
    vector_store = ChromaVectorStore(
        collection_name="neurashield_code_v1",
        persist_directory="phase_1/chroma_db"
    )
    embedding_gen = EmbeddingGenerator()
    analyzer = RAGAnalyzer(
        vector_store=vector_store,
        embedding_generator=embedding_gen,
        llm_model="gpt-4o-mini",  # Fast and cheap model
        top_k=3  # Only retrieve top 3 similar patterns
    )
    
    results = []
    critical_found = False
    
    for file_path in files:
        # Skip non-Python files
        if not file_path.endswith('.py'):
            continue
        
        # Skip if file doesn't exist
        if not os.path.exists(file_path):
            continue
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            continue
        
        # Skip very small files (likely empty or just imports)
        if len(code.strip()) < 50:
            continue
        
        print(f"   Scanning: {file_path}")
        
        # Run analysis - only check for bugs (faster than 'all')
        try:
            analysis = analyzer.analyze_code(code, analysis_type='bugs')
        except Exception as e:
            print(f"   ⚠️  Analysis failed: {e}")
            continue
        
        # Extract risk level
        bug_data = analysis.get('bug_analysis', {})
        risk = bug_data.get('overall_risk', 'unknown')
        bugs = bug_data.get('bugs_found', [])
        
        # Check if critical
        if risk == 'critical':
            critical_found = True
        
        results.append({
            'file': file_path,
            'risk': risk,
            'bugs': len(bugs),
            'details': bugs
        })
    
    return {
        'files': results,
        'has_critical': critical_found
    }


def main():
    """Main entry point"""
    
    # Get list of changed files from git
    changed_files = sys.argv[1:]
    
    # No files to scan
    if not changed_files:
        print("✅ No files to scan")
        sys.exit(0)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set. Skipping NeuraShield scan.")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(0)
    
    # Check if database exists
    db_path = "phase_1/chroma_db"
    if not os.path.exists(db_path):
        print("⚠️  Database not found. Run 'python phase1_pipeline.py' first.")
        sys.exit(0)
    
    print("\n🔍 NeuraShield AI: Scanning staged files...")
    
    # Run scan
    try:
        results = scan_files(changed_files)
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        print("   Allowing commit to proceed")
        sys.exit(0)
    
    # No Python files scanned
    if not results['files']:
        print("✅ No Python files to scan")
        sys.exit(0)
    
    # Print results
    print("\n📊 Scan Results:")
    print("-" * 50)
    
    risk_emoji = {
        'low': '✅',
        'medium': '⚠️ ',
        'high': '🚨',
        'critical': '🔴',
        'unknown': '❓'
    }
    
    for file_result in results['files']:
        emoji = risk_emoji.get(file_result['risk'], '❓')
        print(f"{emoji} {file_result['file']}")
        print(f"   Risk: {file_result['risk'].upper()} | Issues: {file_result['bugs']}")
        
        # Show critical bug details
        if file_result['risk'] in ['critical', 'high'] and file_result['details']:
            for bug in file_result['details'][:2]:  # Show max 2 bugs
                print(f"   - {bug.get('type', 'Issue')}: {bug.get('description', 'No description')[:80]}")
    
    print("-" * 50)
    
    # Block commit if critical issues found
    if results['has_critical']:
        print("\n🔴 CRITICAL vulnerabilities found! Commit BLOCKED.")
        print("   Fix issues or use 'git commit --no-verify' to bypass")
        sys.exit(1)  # Non-zero exit code blocks the commit
    
    print("\n✅ Pre-commit scan passed!")
    sys.exit(0)  # Zero exit code allows the commit


if __name__ == '__main__':
    main()
