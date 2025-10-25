
import ast
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import tempfile
import shutil
import subprocess


class GitHubCodeExtractor:
    def __init__(self, repo_url: str, target_dir: Optional[str] = None):
        self.repo_url = repo_url
        self.target_dir = target_dir or tempfile.mkdtemp()
        self.repo_path = None

    def clone_repository(self) -> Path:
        try:
            subprocess.run(
                ['git', 'clone', self.repo_url, self.target_dir], 
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            self.repo_path = Path(self.target_dir)
            return self.repo_path
        except Exception as e:
            raise RuntimeError(f"Failed to clone repository: {e}")

    def extract_python_files(self) -> List[Dict]:
        if not self.repo_path:
            self.clone_repository()

        exclude_dirs = {'venv', 'env', '.venv', 'node_modules', '.git', '__pycache__', '.pytest_cache', 'tests', 'test'}
        python_files = [f for f in self.repo_path.rglob('*.py') if not any(exclude in f.parts for exclude in exclude_dirs)]

        code_files = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    source_code = f.read()

                if not source_code.strip():
                    continue

                tree = ast.parse(source_code, filename=str(py_file))

                functions = [
                    {
                        'name': node.name,
                        'line_start': node.lineno,
                        'line_end': node.end_lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'args': [arg.arg for arg in node.args.args]
                    }
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]

                classes = [
                    {
                        'name': node.name,
                        'line_start': node.lineno,
                        'line_end': node.end_lineno,
                        'methods': [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    }
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                ]

                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(node.module or '')

                loc = len([line for line in source_code.splitlines() if line.strip()])

                code_files.append({
                    'file_path': str(py_file.relative_to(self.repo_path)),
                    'absolute_path': str(py_file),
                    'source_code': source_code,
                    'functions': functions,
                    'classes': classes,
                    'imports': imports,
                    'loc': loc,
                    'language': 'python'
                })

            except (SyntaxError, Exception):
                continue

        return code_files

    def save_to_json(self, code_files: List[Dict], output_file: str = "extracted_code.json"):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(code_files, f, indent=2, ensure_ascii=False)

    def cleanup(self):
        if self.target_dir and os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)


if __name__ == "__main__":
    repo_url = "https://github.com/sea-bass/python-testing-ci"
    extractor = GitHubCodeExtractor(repo_url)
    code_files = extractor.extract_python_files()
    extractor.save_to_json(code_files, output_file="phase_1/extracted_code.json")

    print(f"Files: {len(code_files)} | LOC: {sum(f['loc'] for f in code_files):,} | Functions: {sum(len(f['functions']) for f in code_files)}")