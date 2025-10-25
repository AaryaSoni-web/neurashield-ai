def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)

api_key = "sk-1234567890abcdef"
