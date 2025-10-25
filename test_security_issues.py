"""
Test file with intentional security vulnerabilities
"""

def insecure_login(username, password):
    # Hardcoded credentials
    admin_password = "admin123"
    
    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    return execute_query(query)


def unsafe_code_execution(user_input):
    # Code injection vulnerability
    result = eval(user_input)
    return result


def read_user_file(filename):
    # Path traversal vulnerability
    with open("/var/data/" + filename) as f:
        return f.read()
