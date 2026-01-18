from ninja import Router
from django.db.models import Count, Q
from .models import Trial, HealeyTrial
from typing import List, Dict, Any, Optional
import datetime

router = Router()

import jwt
import time
import os

@router.get("/metabase-token")
def get_metabase_token(request):
    """Generates a signed JWT for Metabase embedding."""
    METABASE_SECRET_KEY = os.getenv("METABASE_SECRET_KEY")
    DASHBOARD_ID = 2 # Hardcoded for now based on user request
    
    if not METABASE_SECRET_KEY:
        return {"error": "Metabase Secret Key not configured"}

    payload = {
      "resource": {"dashboard": DASHBOARD_ID},
      "params": {},
      "exp": round(time.time()) + (60 * 60) # 1 hour expiration
    }
    
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
    return {"token": token}

@router.get("/summary")
def get_analytics_summary(request):
    total_trials = Trial.objects.count()
    
    # Active status list matching DB normalization
    active_statuses = ['RECRUITING', 'ENROLLING_BY_INVITATION', 'ACTIVE_NOT_RECRUITING', 'AVAILABLE', 'APPROVED_FOR_MARKETING']
    active_trials = Trial.objects.filter(overall_status__in=active_statuses).count()
    
    # Total enrollment (sum of enrollment_count where available)
    # Using aggregate could be faster, but direct sum is fine for now
    total_enrollment_data = Trial.objects.exclude(enrollment_count__isnull=True).aggregate(total=Count('enrollment_count')) # Wait, Count is just count of rows. We need Sum.
    # Actually, let's use Sum
    from django.db.models import Sum
    enrollment_agg = Trial.objects.aggregate(total_enrollment=Sum('enrollment_count'))
    total_enrollment = enrollment_agg['total_enrollment'] or 0

    return {
        "total_trials": total_trials,
        "active_trials": active_trials,
        "total_enrollment": total_enrollment
    }

@router.get("/trials-by-phase")
def get_trials_by_phase(request):
    # Group by study_phase and count
    # Data cleanliness is an issue (strings vs lists), but let's assume raw string or cleaned string in DB
    # If study_phase is a CharField, easy. If JSON, might be tricky.
    # Model says: study_phase = models.CharField(max_length=50, ...)
    # So simple aggregation works.
    
    data = Trial.objects.values('study_phase').annotate(count=Count('unique_protocol_id')).order_by('-count')
    # Filter out None/Empty if needed, or handle in frontend
    formatted = [{"name": item['study_phase'] or "Unknown", "value": item['count']} for item in data]
    return formatted

@router.get("/trials-by-status")
def get_trials_by_status(request):
    data = Trial.objects.values('overall_status').annotate(count=Count('unique_protocol_id')).order_by('-count')
    formatted = [{"name": item['overall_status'] or "Unknown", "value": item['count']} for item in data]
    return formatted

@router.get("/enrollment-stats")
def get_enrollment_stats(request):
    # Top 10 trials by enrollment
    top_trials = Trial.objects.exclude(enrollment_count__isnull=True).order_by('-enrollment_count')[:10]
    formatted = [
        {
            "name": t.brief_title[:50] + "..." if t.brief_title and len(t.brief_title) > 50 else (t.brief_title or t.unique_protocol_id),
            "value": t.enrollment_count,
            "id": t.unique_protocol_id
        }
        for t in top_trials
    ]
    return formatted
