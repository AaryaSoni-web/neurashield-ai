# Test file with intentional vulnerability
def get_user(user_id):
    # SQL Injection - using string concatenation
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    return execute_query(query)

def unsafe_eval(code):
    # Code Injection - using eval
    result = eval(code)
    return result
