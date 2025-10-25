"""
Test file to verify NeuraShield PR scanning works
Contains intentional security vulnerabilities
"""
import os

# VULNERABILITY 1: Hardcoded credentials
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

def authenticate_user(username, password):
    # VULNERABILITY 2: SQL Injection
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    return execute_query(query)

def run_command(user_input):
    # VULNERABILITY 3: Command Injection
    os.system("ls " + user_input)

def evaluate_expression(expr):
    # VULNERABILITY 4:Code Injection
    return eval(expr)

def read_file(filename):
    # VULNERABILITY 5: Path Traversal
    path = "/var/data/" + filename
    with open(path) as f:
        return f.read()
