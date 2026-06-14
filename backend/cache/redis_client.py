import redis
import json
from backend.config import Config
redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
def get_cache(key):
    try:
        val = redis_client.get(key)
        return json.loads(val) if val else None
    except: return None
def set_cache(key, val, expiry=Config.CACHE_EXPIRY):
    try:
        redis_client.setex(key, expiry, json.dumps(val))
        return True
    except: return False
def delete_cache(key):
    try: return redis_client.delete(key)
    except: return False
def delete_pattern(pat):
    try:
        keys = redis_client.keys(pat)
        if keys: redis_client.delete(*keys)
        return True
    except: return False
def get_departments_cache_key(): return "departments:all"
def get_doctor_cache_key(did): return f"doctor:{did}"
def get_doctors_by_specialization_key(sid): return f"doctors:specialization:{sid}"
def get_admin_stats_key(): return "admin:stats"
def get_doctor_stats_key(did): return f"doctor:{did}:stats"
def invalidate_department_cache(): delete_cache(get_departments_cache_key())
def invalidate_doctor_cache(did=None):
    if did: delete_cache(get_doctor_cache_key(did))
    delete_pattern("doctors:*")
    delete_cache(get_admin_stats_key())
def invalidate_appointment_cache():
    delete_pattern("doctor:*:stats")
    delete_cache(get_admin_stats_key())
