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
