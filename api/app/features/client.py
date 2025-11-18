import os, json, time
from typing import List, Dict

from app.core.config import settings

# Try to import redis, otherwise fall back to an in-memory stub
try:
    import redis
    _HAS_REDIS = True
except Exception:
    _HAS_REDIS = False
    class _RedisStub:
        def __init__(self, *args, **kwargs):
            self.store = {}
        def get(self, k):
            return self.store.get(k)
        def set(self, k, v):
            self.store[k] = v
    redis = _RedisStub

class FeatureClient:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        if _HAS_REDIS:
            self.redis = redis.Redis(host=os.environ.get('REDIS_HOST', settings.redis_host),
                                     port=int(os.environ.get('REDIS_PORT', settings.redis_port)),
                                     decode_responses=True)
        else:
            # in-memory redis-like object
            self.redis = redis()

    def get_features(self, services: List[str]) -> Dict[str, float]:
        svc = services[0] if services else 'unknown'
        prefix = f"feature:{self.tenant_id}:{svc}:"
        try:
            error_rate = float(self.redis.get(prefix + 'error_rate_5m') or 0.0)
            p95 = float(self.redis.get(prefix + 'p95_latency_5m') or 0.0)
        except Exception:
            error_rate = 0.0
            p95 = 0.0
        return {'error_rate_5m': error_rate, 'p95_latency_5m': p95}
