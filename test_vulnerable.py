def get_user(user_id):
    # SQL Injection - CRITICAL vulnerability
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)

def authenticate(username, password):
    # Hardcoded credentials - CRITICAL
    api_key = "sk-1234567890abcdef"
    return True
