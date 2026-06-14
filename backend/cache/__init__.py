from .redis_client import (
    redis_client,
    get_cache,
    set_cache,
    delete_cache,
    delete_pattern,
    get_departments_cache_key,
    get_doctor_cache_key,
    get_doctors_by_specialization_key,
    get_admin_stats_key,
    get_doctor_stats_key,
    invalidate_department_cache,
    invalidate_doctor_cache,
    invalidate_appointment_cache
)
