from datetime import datetime, timedelta
import jwt, os
SECRET = os.environ.get('ASTERIA_JWT_SECRET','devsecret')
def create_token(tenant_id:str, role='admin', expires_minutes=60):
    payload = {'tenant':tenant_id, 'role':role, 'exp': datetime.utcnow() + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, SECRET, algorithm='HS256')
def decode_token(token:str):
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'])
    except Exception as e:
        return None
