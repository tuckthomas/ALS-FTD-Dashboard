from ninja import Router, Schema, Query
from django.db.models import Count, Q, Sum, Avg
from django.db.models.functions import ExtractYear
from django.core.cache import cache
from .models import Trial, HealeyTrial, Gene, NewsArticle
from typing import List, Dict, Any, Optional
import datetime
import json
import re

router = Router()





def apply_analytics_filters(queryset, status: List[str] = None, phase: List[str] = None, gene: str = None, familial: bool = False):
    """Reusable filter logic for analytics endpoints."""
    if status:
        status_map = {
            'recruiting': ['RECRUITING', 'ENROLLING_BY_INVITATION'],
            'active': ['ACTIVE_NOT_RECRUITING'],
            'completed': ['COMPLETED'],
            # Actionable/Active trials for patients
            'active_all': ['RECRUITING', 'ENROLLING_BY_INVITATION', 'NOT_YET_RECRUITING', 'AVAILABLE'],
            'inactive': ['COMPLETED', 'TERMINATED', 'WITHDRAWN', 'SUSPENDED', 'UNKNOWN', 'NO_LONGER_AVAILABLE']
        }
        
        combined_statuses = []
        for s in status:
            combined_statuses.extend(status_map.get(s.lower(), [s.upper()]))
            
        queryset = queryset.filter(overall_status__in=combined_statuses)
        
    if phase:
        queryset = queryset.filter(study_phase__in=phase)
        
    if gene:
         queryset = queryset.filter(
            Q(related_genes__gene_symbol__iexact=gene) | 
            Q(genes__icontains=gene)
        ).distinct()
    
    if familial:
        queryset = queryset.filter(
            Q(related_genes__isnull=False) | 
            (~Q(genes=[]) & ~Q(genes__isnull=True))
        ).distinct()
        
    return queryset

@router.get("/countries")
def get_countries(request):
    """Returns a list of unique countries found in study locations."""
    # Fetch all study locations
    # We use iterator to avoid loading everything into memory at once if possible, 
    # though for 1.2k records it's negligible.
    trials = Trial.objects.exclude(study_location__isnull=True).values_list('study_location', flat=True)
    
    countries = set()
    for locations in trials:
        if not locations:
            continue
            
        # Handle if it's a list (standard) or single dict
        loc_list = locations if isinstance(locations, list) else [locations]
        
        for loc in loc_list:
            if isinstance(loc, dict):
                # Check common keys for country
                c = loc.get('country') or loc.get('LocationCountry')
                if c:
                    countries.add(c.strip())
                    
    # Sort alphabetically
    return sorted(list(countries))

@router.get("/summary")
def get_analytics_summary(request):
    total_trials = Trial.objects.count()
    
    # Active status list matching DB normalization (Actionable trials)
    active_statuses = ['RECRUITING', 'ENROLLING_BY_INVITATION', 'NOT_YET_RECRUITING', 'AVAILABLE']
    active_trials = Trial.objects.filter(overall_status__in=active_statuses).count()
    
    enrollment_agg = Trial.objects.aggregate(total_enrollment=Sum('enrollment_count'))
    total_enrollment = enrollment_agg['total_enrollment'] or 0

    return {
        "total_trials": total_trials,
        "active_trials": active_trials,
        "total_enrollment": total_enrollment
    }

def get_full_trials_dataset():
    """
    Fetches, serializes, and caches the complete trials dataset.
    Used by:
    1. get_trials_list (lazy load)
    2. Management command (proactive refresh)
    """
    print("Generating full dataset cache...")
    raw_trials = Trial.objects.all()
    # Pre-fetch related genes and status to avoid N+1
    raw_trials = raw_trials.prefetch_related('related_genes', 'status')
    
    result = []
    for t in raw_trials:
        # Determine Status
        mapped_status = 'Unknown'
        
        # Prefer normalized M2M status if available
        normalized_status = t.status.first()
        if normalized_status:
            # Apply Title Case to the mapped name to ensure "Proper Capitalization"
            mapped_status = normalized_status.name.replace('_', ' ').title()
        else:
            # Fallback to string logic for unmapped legacy statuses
            s_raw = (t.overall_status or '').replace('_', ' ').title()
            if s_raw:
                mapped_status = s_raw
            else:
                mapped_status = 'Unknown'
        
        # Last Updated
        last_updated = 'N/A'
        if t.status_verified_date:
            if isinstance(t.status_verified_date, datetime.date):
                last_updated = t.status_verified_date.strftime('%Y-%m-%d')
            else:
                 last_updated = str(t.status_verified_date)

        # Eligibility
        eligibility = []
        if t.eligibility_criteria_inclusion_description:
            try:
                incl = t.eligibility_criteria_inclusion_description
                if isinstance(incl, str):
                    incl = json.loads(incl)
                if isinstance(incl, list):
                    eligibility = incl[:5]
            except:
                pass
        
        # Summary
        summary = ''
        if t.brief_description:
            summary = t.brief_description
        elif t.study_population:
            # Keep fallback reasonable or full length? Let's default to full length for now as well.
            summary = t.study_population
        
        # Derived Intervention Types
        intervention_types = set()
        if t.intervention_name and isinstance(t.intervention_name, list):
            for i in t.intervention_name:
                if isinstance(i, dict) and 'type' in i:
                    intervention_types.add(i['type'])
        
        if not intervention_types and t.intervention_types:
             if isinstance(t.intervention_types, list):
                 intervention_types.update(t.intervention_types)
        
        # Genes: Strip 'Mutation' suffix more aggressively
        raw_genes = [g.gene_symbol for g in t.related_genes.all()]
        if t.genes and isinstance(t.genes, list):
            raw_genes = raw_genes + t.genes
        cleaned_genes = set()
        for g in raw_genes:
            if g:
                # Remove "Mutation" (case-insensitive, with optional whitespace)
                clean = re.sub(r'\s*mutation\s*', '', g, flags=re.IGNORECASE).strip()
                if clean:
                    cleaned_genes.add(clean)

        result.append({
            "id": t.unique_protocol_id,
            "nctId": t.nct_id,
            "title": t.brief_title or t.unique_protocol_id,
            "sponsor": t.lead_sponsor_name or 'Unknown',
            "status": mapped_status, 
            "phase": 'NA' if not t.study_phase or t.study_phase.upper() == 'NA' else t.study_phase,
            "studyType": ('NA' if not t.study_type or t.study_type.upper() == 'NA' else t.study_type).replace('_', ' ').title(),
            "interventionTypes": sorted(list(intervention_types)),
            "lastUpdated": last_updated,
            "genes": sorted(list(cleaned_genes)),
            "summary": summary,
            "eligibility": eligibility,
            "enrollment": t.enrollment_count,
            "url": t.clinical_trial_url,
            "startDate": str(t.study_start_date) if t.study_start_date else None,
            "completionDate": str(t.completion_date) if t.completion_date else None,
            "locations": t.study_location if isinstance(t.study_location, list) else [],
            "investigator": t.responsible_party_investigator_full_name,
        })
        
    response_data = {
        "trials": result,
        "pagination": {
            "page": 1,
            "per_page": -1,
            "total_count": len(result),
            "total_pages": 1,
        }
    }
    
    # Cache indefinitely (until next manual refresh)
    cache.set('api_trials_list_full', response_data, timeout=None)
    return response_data

@router.get("/dashboard-stats")
def get_dashboard_stats(request, status: List[str] = Query(None), phase: List[str] = Query(None), gene: str = None, familial: bool = False):
    """Combined stats for dashboard stat cards."""
    queryset = Trial.objects.all()
    queryset = apply_analytics_filters(queryset, status, phase, gene, familial)
    
    # Total participants (sum of enrollment)
    # Refined: We restrict ALL stats to INTERVENTIONAL trials for consistency.
    interventional_queryset = queryset.filter(study_type__iexact='INTERVENTIONAL')
    
    total_trials = interventional_queryset.count()
    
    enrollment_agg = interventional_queryset.aggregate(total_enrollment=Sum('enrollment_count'))
    total_participants = enrollment_agg['total_enrollment'] or 0
    
    # Clinical sites - count unique locations from study_location JSON
    # Count unique locations for interventional trials only
    trials_with_locations = interventional_queryset.exclude(study_location__isnull=True)
    site_count = 0
    for trial in trials_with_locations:
        if trial.study_location:
            try:
                locations = trial.study_location if isinstance(trial.study_location, list) else []
                site_count += len(locations)
            except:
                pass
    
    # Median enrollment rate (robust against outliers)
    # Filtered to interventional only
    trials_with_enrollment = interventional_queryset.exclude(enrollment_count__isnull=True).exclude(enrollment_count=0)
    enrollment_values = list(trials_with_enrollment.values_list('enrollment_count', flat=True))
    
    avg_enrollment = 0
    if enrollment_values:
        import statistics
        avg_enrollment = statistics.median(enrollment_values)
    
    # Calculate recruiting percentage relative to the *filtered* set
    active_statuses = ['RECRUITING', 'ENROLLING_BY_INVITATION']
    recruiting_count = interventional_queryset.filter(overall_status__in=active_statuses).count()
    total_interventional = total_trials # Already calculated above
    recruiting_pct = round((recruiting_count / total_interventional * 100), 1) if total_interventional > 0 else 0
    
    return {
        "total_trials": total_trials,
        "total_participants": total_participants,
        "clinical_sites": site_count,
        "avg_enrollment": round(avg_enrollment, 0),
        "recruiting_percentage": recruiting_pct
    }

@router.get("/trials-by-phase")
def get_trials_by_phase(request, status: List[str] = None, phase: List[str] = None, gene: str = None, familial: bool = False):
    queryset = Trial.objects.all()
    queryset = apply_analytics_filters(queryset, status, phase, gene, familial)
    
    data = queryset.values('study_phase').annotate(count=Count('unique_protocol_id')).order_by('-count')
    formatted = [{"name": item['study_phase'] or "Unknown", "value": item['count']} for item in data]
    return formatted

@router.get("/trials-by-status")
def get_trials_by_status(request, status: List[str] = None, phase: List[str] = None, gene: str = None, familial: bool = False):
    """Returns trial counts by status, formatted for donut chart."""
    queryset = Trial.objects.all()
    queryset = apply_analytics_filters(queryset, status, phase, gene, familial)
    
    # improved query performance: aggregate by normalized status name
    data = queryset.values('overall_status').annotate(count=Count('unique_protocol_id')).order_by('-count')
    # Filter out empty status if any
    data = [d for d in data if d['overall_status']]
    
    formatted = [{"name": item['overall_status'], "value": item['count']} for item in data]
    return formatted

def _get_active_trials_list():
    """
    Helper to return the list of active trials.
    Single source of truth for both the list view and the filters.
    """
    full_data = get_full_trials_dataset()
    
    # Exclusion List logic
    excluded_statuses = [
        'Completed', 'Terminated', 'Withdrawn', 'Suspended', 
        'Active, Not Recruiting', 'Active Not Recruiting', 'Active_Not_Recruiting', 
        'Unknown',
        'No Longer Available',
        'Temporarily Not Available'
    ]
    
    # Filter active trials based on the serialized 'status' field (which is already normalized/mapped)
    active_trials = [
        t for t in full_data['trials'] 
        if t['status'] not in excluded_statuses
    ]
    return active_trials

@router.get("/filter-options")
def get_filter_options(request):
    """
    Returns distinct values for dynamic filters:
    - Phases
    - Study Types
    - Statuses
    - Genes
    derived DYNAMICALLY from the active dataset.
    """
    active_trials = _get_active_trials_list()
    
    # Extract unique values using Python sets
    phases = set()
    study_types = set()
    statuses = set()
    genes = set()
    intervention_types = set()
    
    for t in active_trials:
        if t.get('phase'):
            phases.add(t['phase'])
        if t.get('studyType'):
            study_types.add(t['studyType'])
        if t.get('status'):
            statuses.add(t['status'])
        
        # Genes can be in 'genes' list
        # Redundant cleaning just in case
        if t.get('genes'):
            for g in t['genes']:
                clean_g = re.sub(r'\s*mutation\s*', '', g, flags=re.IGNORECASE).strip()
                genes.add(clean_g)

        # Intervention Types
        if t.get('interventionTypes'):
            for it in t['interventionTypes']:
                # Clean up: replace underscores with spaces and Title Case
                clean_type = it.replace('_', ' ').title()
                intervention_types.add(clean_type)
        else:
            # Add explicit "Not Specified" if missing or empty
            intervention_types.add("Not Specified")

    return {
        "phases": sorted(list(phases)),
        "study_types": sorted(list(study_types)),
        "statuses": sorted(list(statuses)),
        "genes": sorted(list(genes)),
        "intervention_types": sorted(list(intervention_types))
    }


@router.get("/funding-sources")
def get_funding_sources(request, status: List[str] = None, phase: List[str] = None, gene: str = None, familial: bool = False):
    """Returns trial counts by lead sponsor, grouped into categories."""
    queryset = Trial.objects.all()
    queryset = apply_analytics_filters(queryset, status, phase, gene, familial)
    
    data = queryset.values('lead_sponsor_name').annotate(count=Count('unique_protocol_id')).order_by('-count')
    
    # Categorize sponsors
    categories = {
        'NIH/Federal': 0,
        'Industry': 0,
        'Academic': 0,
        'Other': 0
    }
    
    federal_keywords = ['nih', 'national institutes', 'national institute', 'federal', 'government', 'va ', 'veterans']
    industry_keywords = ['pharma', 'therapeutics', 'inc', 'corp', 'ltd', 'llc', 'biogen', 'novartis', 'roche', 'pfizer', 'sanofi', 'lilly', 'gsk', 'astrazeneca']
    academic_keywords = ['university', 'college', 'hospital', 'medical center', 'school of medicine', 'institute', 'foundation']
    
    for item in data:
        sponsor = (item['lead_sponsor_name'] or '').lower()
        count = item['count']
        
        if any(kw in sponsor for kw in federal_keywords):
            categories['NIH/Federal'] += count
        elif any(kw in sponsor for kw in industry_keywords):
            categories['Industry'] += count
        elif any(kw in sponsor for kw in academic_keywords):
            categories['Academic'] += count
        else:
            categories['Other'] += count
    
    # Calculate percentages
    total = sum(categories.values())
    result = []
    for name, count in categories.items():
        pct = round((count / total * 100), 0) if total > 0 else 0
        result.append({"name": name, "value": count, "percentage": pct})
    
    # Sort by value descending
    result.sort(key=lambda x: x['value'], reverse=True)
    return result

@router.get("/geographic-distribution")
def get_geographic_distribution(request, status: List[str] = None, phase: List[str] = None, gene: str = None, familial: bool = False):
    """Returns trial counts by country."""
    queryset = Trial.objects.all()
    queryset = apply_analytics_filters(queryset, status, phase, gene, familial)
    
    # Limit to filtered trials
    trials = queryset.exclude(study_location__isnull=True).values('study_location')
    country_counts = {}
    
    # Pre-compiled mapping for normalization (optional, but good for data cleanliness)
    # Basic normalization to Title Case
    
    for t in trials:
        locs = t['study_location']
        if not locs: continue
        
        # Handle if it's a string (serialization artifact)
        if isinstance(locs, str):
            try:
                locs = json.loads(locs)
            except:
                continue
                
        visited_countries_for_this_trial = set()
        if isinstance(locs, list):
            for loc in locs:
                if isinstance(loc, dict):
                    c = (loc.get('country') or loc.get('LocationCountry') or '').strip()
                    if c:
                        # Normalize typical variations if needed, or just Title Case
                        c_norm = c.title() 
                        # Specific fixes for common variations could go here e.g. "Korea, Republic of" -> "South Korea"
                        # But for now, raw accurate country names are better than arbitrary regions.
                        
                        if c_norm not in visited_countries_for_this_trial:
                            country_counts[c_norm] = country_counts.get(c_norm, 0) + 1
                            visited_countries_for_this_trial.add(c_norm)

    # Return top 20 or all? User wants accurate data. Let's return all, sorted.
    # Frontend map likely handles "Rest of world" or specific list.
    # Note: Frontend currently might expect "North America" etc. if the map is hardcoded to regions.
    # I should check the frontend map component quickly to see if it breaks. 
    # BUT FIRST: Fix the backend data.
    
    result = [{"name": name, "value": count} for name, count in country_counts.items()]
    result.sort(key=lambda x: x['value'], reverse=True)
    return result

@router.get("/genetic-markers")
def get_genetic_markers(request, status: List[str] = None, phase: List[str] = None, gene: str = None, familial: bool = False):
    """Returns trial counts and drug counts by genetic marker/gene."""
    # 1. Get the filtered set of trials first
    queryset = Trial.objects.all()
    
    # Default to "Active/Actionable" ONLY if status is None (not provided)
    # If status is [] (explicit empty list), it means "All", so we skip filtering
    target_status = ['active_all'] if status is None else status
    queryset = apply_analytics_filters(queryset, target_status, phase, gene, familial)
    
    # Get IDs to ensure sub-queries in Count() are accurate
    active_trial_ids = list(queryset.values_list('unique_protocol_id', flat=True))
    
    # 2. Annotate Genes based on this specific trial set
    genes = Gene.objects.exclude(
        gene_risk_category__iexact='Tenuous'
    ).annotate(
        # Number of unique trials for this gene in the active set
        trial_count=Count('trials', filter=Q(trials__unique_protocol_id__in=active_trial_ids), distinct=True),
        # Number of unique trials for this gene that HAVE a Drug intervention
        drug_count=Count('trials', filter=Q(trials__unique_protocol_id__in=active_trial_ids) & Q(trials__interventions__intervention_type__icontains='Drug'), distinct=True),
        # Interventional vs Observational breakdown
        interventional_count=Count('trials', filter=Q(trials__unique_protocol_id__in=active_trial_ids) & Q(trials__study_type__iexact='Interventional'), distinct=True),
        observational_count=Count('trials', filter=Q(trials__unique_protocol_id__in=active_trial_ids) & Q(trials__study_type__iexact='Observational'), distinct=True)
    ).order_by('-trial_count')
    
    result = []
    for gene in genes:
        name = re.sub(r'\s*mutation\s*', '', gene.gene_symbol, flags=re.IGNORECASE).strip()
        result.append({
            "name": name,
            "full_name": gene.gene_name,
            "category": gene.gene_risk_category,
            "trials": gene.trial_count,
            "drugs": gene.drug_count,
            "interventional": gene.interventional_count,
            "observational": gene.observational_count
        })
    
    return result

@router.get("/enrollment-stats")
def get_enrollment_stats(request, status: List[str] = None, phase: List[str] = None, gene: str = None, familial: bool = False):
    queryset = Trial.objects.all()
    queryset = apply_analytics_filters(queryset, status, phase, gene, familial)
    
    # Top 10 trials by enrollment
    top_trials = queryset.exclude(enrollment_count__isnull=True).order_by('-enrollment_count')[:10]
    formatted = [
        {
            "name": t.brief_title[:50] + "..." if t.brief_title and len(t.brief_title) > 50 else (t.brief_title or t.unique_protocol_id),
            "value": t.enrollment_count,
            "id": t.unique_protocol_id
        }
        for t in top_trials
    ]
    return formatted


@router.get("/latest-news")
def get_latest_news(request):
    """Returns the 3 most recent news articles."""
    articles = NewsArticle.objects.order_by('-publication_date')[:3]
    return [
        {
            "title": a.title,
            "source": a.source_name,
            "date": a.publication_date.strftime('%b %d'),
            "url": a.url
        }
        for a in articles
    ]

@router.get("/dashboard-package")
def get_dashboard_package(request, familial: bool = False):
    """Returns all data needed for the dashboard in a single request."""
    cache_key = f'dashboard_package_familial_v2_{familial}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data

    data = {
        "stats": get_dashboard_stats(request, status=None, phase=None, gene=None, familial=familial),
        "active_stats": get_dashboard_stats(request, status=['active_all'], phase=None, gene=None, familial=familial),
        "status_data": get_trials_by_status(request, status=None, phase=None, gene=None, familial=familial),
        "funding_data": get_funding_sources(request, status=None, phase=None, gene=None, familial=familial),
        "geo_data": get_geographic_distribution(request, status=None, phase=None, gene=None, familial=familial),
        "gene_data": get_genetic_markers(request, status=None, phase=None, gene=None, familial=familial), # Active (default)
        "historical_gene_data": get_genetic_markers(request, status=[], phase=None, gene=None, familial=familial), # All Time (explicit empty status)
        "year_data": get_trials_by_year(request, status=None, phase=None, gene=None, country=None, familial=familial),
        "map_data": get_global_map_data(request, status=None, phase=None, gene=None, familial=familial),
        "news_data": get_latest_news(request)
    }
    
    # Cache indefinitely (until next manual refresh)
    cache.set(cache_key, data, timeout=None)
    return data

@router.get("/trial-finder-data")
def get_trial_finder_data(request):
    """
    Dedicated endpoint for the Client-Side Trial Finder.
    Returns ONLY active/recruiting/pending trials.
    Derived from _get_active_trials_list for consistency.
    """
    active_trials = _get_active_trials_list()
    
    return {
        "trials": active_trials,
        "total_count": len(active_trials),
        "note": "Excludes Completed/Terminated/Withdrawn/Suspended/Active, Not Recruiting/No Longer Available"
    }

@router.get("/trials-list")
def get_trials_list(request, 
                   page: int = 1, 
                   per_page: int = 25,
                   status: List[str] = Query(None), 
                   phase: List[str] = Query(None), 
                   study_type: List[str] = Query(None), 
                   gene: str = None,
                   sort_by: str = '-status_verified_date'):

    """Paginated list of trials for the Trial Finder page."""
    # Check cache for "all trials" request (no filters, per_page=-1)
    is_full_fetch = (
        per_page == -1 and 
        not any([status, phase, gene, study_type, search, country])
    )
    
    cache_key = 'api_trials_list_full'
    if is_full_fetch:
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        # If not in cache, generate it now
        return get_full_trials_dataset()

    queryset = Trial.objects.all()
    
    # Apply filters
    if status:
        status_map = {
            'recruiting': ['RECRUITING', 'ENROLLING_BY_INVITATION'],
            'active': ['ACTIVE_NOT_RECRUITING'],
            'completed': ['COMPLETED'],
        }
        statuses = status_map.get(status.lower(), [status.upper()])
        queryset = queryset.filter(overall_status__in=statuses)

    if study_type:
        queryset = queryset.filter(study_type__iexact=study_type)
    
    if phase:
        # Handle multiple phases
        # We use strict matching because the values are standardized (Phase 1, Phase 2, etc.)
        queryset = queryset.filter(study_phase__in=phase)
    
    if gene:
        # Filter by gene (related_genes M2M or genes JSON field)
        queryset = queryset.filter(
            Q(related_genes__gene_symbol__iexact=gene) | 
            Q(genes__icontains=gene)
        ).distinct()
    
    if search:
        queryset = queryset.filter(
            Q(brief_title__icontains=search) |
            Q(nct_id__icontains=search) |
            Q(lead_sponsor_name__icontains=search)
        )
    
    if country:
        queryset = queryset.filter(study_location__icontains=country)
    
    # Sorting
    if sort_by:
        field_map = {
            'title': 'brief_title',
            'status': 'overall_status',
            'phase': 'study_phase',
            'studyType': 'study_type',
            'sponsor': 'lead_sponsor_name',
            'nctId': 'nct_id',
            'lastUpdated': 'last_updated',
            'enrollment': 'enrollment_count'
        }
        db_field = field_map.get(sort_by)
        if db_field:
            if sort_order == 'desc':
                db_field = f'-{db_field}'
            queryset = queryset.order_by(db_field)
    else:
        # Default order
        queryset = queryset.order_by('-status_verified_date', '-study_start_date')
    
    # Get total count for pagination
    total_count = queryset.count()
    
    if per_page == -1:
        # Return all records
        trials = queryset
        total_pages = 1
    else:
        # Apply pagination
        total_pages = (total_count + per_page - 1) // per_page
        offset = (page - 1) * per_page
        trials = queryset[offset:offset + per_page]
    
    # Format response
    result = []
    for t in trials:
        # Map status to simplified version
        status_map_reverse = {
            'RECRUITING': 'recruiting',
            'ENROLLING_BY_INVITATION': 'recruiting',
            'ACTIVE_NOT_RECRUITING': 'active',
            'COMPLETED': 'completed',
            'TERMINATED': 'terminated',
            'WITHDRAWN': 'withdrawn',
            'SUSPENDED': 'suspended',
            'NOT_YET_RECRUITING': 'pending',
        }
        mapped_status = status_map_reverse.get(t.overall_status, 'unknown')
        
        # Get primary intervention type as focus
        focus = 'Interventional'
        if t.intervention_types:
            try:
                types = t.intervention_types if isinstance(t.intervention_types, list) else []
                if types:
                    focus = types[0] if isinstance(types[0], str) else str(types[0])
            except:
                pass
        
        # Format date
        last_updated = ''
        if t.status_verified_date:
            last_updated = t.status_verified_date.strftime('%b %d, %Y')
        elif t.study_start_date:
            last_updated = t.study_start_date.strftime('%b %d, %Y')
        
        # Get eligibility criteria (inclusion)
        eligibility = []
        if t.eligibility_criteria_inclusion_description:
            try:
                incl = t.eligibility_criteria_inclusion_description
                if isinstance(incl, str):
                    incl = json.loads(incl)
                if isinstance(incl, list):
                    eligibility = incl[:5]  # First 5 criteria
            except:
                pass
        
        # Build summary from study_population or first part of eligibility
        summary = ''
        if t.study_population:
            summary = t.study_population[:500]
        
        result.append({
            "id": t.unique_protocol_id,
            "nctId": t.nct_id,
            "title": t.brief_title or t.unique_protocol_id,
            "sponsor": t.lead_sponsor_name or 'Unknown',
            "status": mapped_status,
            "phase": t.study_phase or 'N/A',
            "studyType": t.study_type or 'N/A',
            "lastUpdated": last_updated,
            "summary": summary,
            "eligibility": eligibility,
            "enrollment": t.enrollment_count,
            "url": t.clinical_trial_url,
        })
    
    return {
        "trials": result,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
        }
    }


# =============================================================================
# QUERY BUILDER ENDPOINT
# =============================================================================

# Whitelist of allowed fields for querying
ALLOWED_QUERY_FIELDS = {
    'nct_id': 'nct_id',
    'brief_title': 'brief_title',
    'overall_status': 'overall_status',
    'study_phase': 'study_phase',
    'lead_sponsor_name': 'lead_sponsor_name',
    'enrollment_count': 'enrollment_count',
    'study_start_date': 'study_start_date',
    'genes': 'genes',
    'study_location': 'study_location',
}

# Allowed operators
ALLOWED_OPERATORS = ['equals', 'contains', 'starts_with', 'gt', 'lt', 'gte', 'lte']


@router.post("/query")
def execute_query(request):
    """
    Execute a safe query built by the Query Builder.
    Uses Django ORM only - no raw SQL.
    """
    try:
        import json as json_module
        body = json_module.loads(request.body)
    except:
        return {"error": "Invalid JSON body"}
    
    filters = body.get('filters', [])
    logic = body.get('logic', 'AND')
    limit = min(body.get('limit', 100), 1000)  # Max 1000 results
    
    # Validate and build query
    queryset = Trial.objects.all()
    q_objects = []
    
    for f in filters:
        field = f.get('field')
        operator = f.get('operator')
        value = f.get('value', '')
        
        # Validate field
        if field not in ALLOWED_QUERY_FIELDS:
            return {"error": f"Invalid field: {field}"}
        
        # Validate operator
        if operator not in ALLOWED_OPERATORS:
            return {"error": f"Invalid operator: {operator}"}
        
        db_field = ALLOWED_QUERY_FIELDS[field]
        
        # Build Q object based on operator
        if operator == 'equals':
            q_objects.append(Q(**{db_field: value}))
        elif operator == 'contains':
            q_objects.append(Q(**{f'{db_field}__icontains': value}))
        elif operator == 'starts_with':
            q_objects.append(Q(**{f'{db_field}__istartswith': value}))
        elif operator == 'gt':
            try:
                q_objects.append(Q(**{f'{db_field}__gt': float(value)}))
            except ValueError:
                q_objects.append(Q(**{f'{db_field}__gt': value}))
        elif operator == 'lt':
            try:
                q_objects.append(Q(**{f'{db_field}__lt': float(value)}))
            except ValueError:
                q_objects.append(Q(**{f'{db_field}__lt': value}))
        elif operator == 'gte':
            try:
                q_objects.append(Q(**{f'{db_field}__gte': float(value)}))
            except ValueError:
                q_objects.append(Q(**{f'{db_field}__gte': value}))
        elif operator == 'lte':
            try:
                q_objects.append(Q(**{f'{db_field}__lte': float(value)}))
            except ValueError:
                q_objects.append(Q(**{f'{db_field}__lte': value}))
    
    # Combine Q objects with AND or OR
    if q_objects:
        if logic == 'OR':
            combined_q = q_objects[0]
            for q in q_objects[1:]:
                combined_q |= q
        else:  # AND
            combined_q = q_objects[0]
            for q in q_objects[1:]:
                combined_q &= q
        
        queryset = queryset.filter(combined_q)
    
    # Get total count
    total_count = queryset.count()
    
    # Apply limit
    trials = queryset[:limit]
    
    # Build response
    results = []
    for t in trials:
        results.append({
            'nct_id': t.nct_id,
            'title': t.brief_title,
            'status': t.overall_status,
            'phase': t.study_phase,
            'sponsor': t.lead_sponsor_name,
            'enrollment': t.enrollment_count,
            'start_date': str(t.study_start_date) if t.study_start_date else None,
        })
    
    return {
        "results": results,
        "total_count": total_count,
        "returned_count": len(results),
    }

@router.get("/global-map")
def get_global_map_data(request, status: List[str] = None, phase: List[str] = None, gene: str = None, familial: bool = False):
    """
    Returns aggregated trial location data for the global map.
    Grouping by rounded coordinates to cluster nearby sites.
    """
    queryset = Trial.objects.all()
    queryset = apply_analytics_filters(queryset, status, phase, gene, familial)
    
    trials = queryset.exclude(study_location__isnull=True).exclude(study_location={})
    
    # Dictionary to aggregate sites: "lat,lon" -> {data}
    sites = {}
    
    for trial in trials:
        if not trial.study_location or not isinstance(trial.study_location, list):
            continue
            
        for loc in trial.study_location:
            geo = loc.get('geoPoint')
            if not geo or 'lat' not in geo or 'lon' not in geo:
                continue
                
            try:
                lat = float(geo['lat'])
                lon = float(geo['lon'])
                
                # Create a key for grouping (rounding to 3 decimal places ~100m)
                key = f"{round(lat, 3)},{round(lon, 3)}"
                
                if key not in sites:
                    sites[key] = {
                        "name": loc.get('facility', 'Unknown Facility'),
                        "city": loc.get('city', ''),
                        "country": loc.get('country', ''),
                        "position": [lat, lon],
                        "trial_count": 0,
                        "trials": []
                    }
                
                # Update count and list (avoid duplicates if trial matches multiple locations in same cluster - rare but possible)
                if trial.unique_protocol_id not in [t['id'] for t in sites[key]['trials']]:
                    sites[key]['trial_count'] += 1
                    sites[key]['trials'].append({
                        "id": trial.unique_protocol_id,
                        "title": trial.brief_title
                    })
                    
            except (ValueError, TypeError):
                continue
    
    # Convert to list
    return list(sites.values())


@router.get("/trials-by-year")
def get_trials_by_year(request, status: List[str] = None, phase: List[str] = None, gene: str = None, country: str = None, familial: bool = False):
    """
    Returns trial counts by start year.
    Filters out trials starting after Dec 31st of the previous year.
    """
    current_year = datetime.datetime.now().year
    cutoff_year = current_year - 1
    cutoff_date = datetime.date(cutoff_year, 12, 31)
    
    queryset = Trial.objects.all()
    queryset = apply_analytics_filters(queryset, status, phase, gene, familial)
    
    if country:
        queryset = queryset.filter(study_location__icontains=country)
    
    # Filter trials started on or before the cutoff date
    # Also exclude trials with no start date
    data = (
        queryset
        .filter(study_start_date__lte=cutoff_date)
        .exclude(study_start_date__isnull=True)
        .annotate(year=ExtractYear('study_start_date'))
        .values('year')
        .annotate(count=Count('unique_protocol_id'))
        .order_by('year')
    )
    
    # Format for frontend
    result = [
        {"year": item['year'], "count": item['count']}
        for item in data
        if item['year'] is not None  # Extra safety check
    ]
    
    return result
