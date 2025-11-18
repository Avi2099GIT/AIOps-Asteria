import os, json, redis, time
from typing import List, Dict

from api.app.core.config import settings


class FeatureClient:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.redis = redis.Redis(host=os.environ.get('REDIS_HOST', settings.redis_host),
                                 port=int(os.environ.get('REDIS_PORT', settings.redis_port)),
                                 decode_responses=True)

    def get_features(self, services: List[str]) -> Dict[str, float]:
        # Example: fetch error_rate_5m and p95_latency_5m for first service
        svc = services[0] if services else 'unknown'
        prefix = f"feature:{self.tenant_id}:{svc}:"
        try:
            error_rate = float(self.redis.get(prefix + 'error_rate_5m') or 0.0)
            p95 = float(self.redis.get(prefix + 'p95_latency_5m') or 0.0)
        except Exception:
            error_rate = 0.0
            p95 = 0.0
        return {'error_rate_5m': error_rate, 'p95_latency_5m': p95}
