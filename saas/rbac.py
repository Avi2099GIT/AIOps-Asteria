# Very small RBAC helper
def check_role(token_payload, required_roles):
    if not token_payload: return False
    return token_payload.get('role') in required_roles
