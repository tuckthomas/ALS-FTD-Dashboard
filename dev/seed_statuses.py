import os
import sys
import django

# Setup Django environment
sys.path.append('/root/ALS_FTD_Research_Dashboard')
# Correct the settings module path if project structure is nested
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ALS_FTD_Research_Dashboard.settings')
django.setup()

from Dashboard.models import Trial, TrialStatus

def seed_statuses():
    print("Seeding TrialStatus table...")
    
    # Status definitions provided by user
    statuses = {
        "Not Yet Recruiting": "The study has not started recruiting participants.",
        "Recruiting": "The study is currently recruiting participants.",
        "Enrolling By Invitation": "The study is selecting its participants from a population, or group of people, decided on by the researchers in advance. These studies are not open to everyone who meets the eligibility criteria but only to people in that particular population, who are specifically invited to participate.",
        "Active, Not Recruiting": "The study is ongoing, and participants are receiving an intervention or being examined, but potential participants are not currently being recruited or enrolled.",
        "Suspended": "The study has stopped early but may start again.",
        "Terminated": "The study has stopped early and will not start again. Participants are no longer being examined or treated.",
        "Completed": "The study has ended normally, and participants are no longer being examined or treated (that is, the last participant's last visit has occurred).",
        "Withdrawn": "The study stopped early, before enrolling its first participant.",
        "Unknown": "A study on ClinicalTrials.gov whose last known status was recruiting; not yet recruiting; or active, not recruiting but that has passed its completion date, and the status has not been last verified within the past 2 years."
    }

    # Create Status objects
    status_map = {}
    for name, desc in statuses.items():
        obj, created = TrialStatus.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )
        if created:
            print(f"Created status: {name}")
        else:
            # Update description if needed
            if obj.description != desc:
                obj.description = desc
                obj.save()
                print(f"Updated description for: {name}")
        status_map[name.lower()] = obj

    print("\nBackfilling Trial statuses...")
    
    # Batch update/backfill
    trials = Trial.objects.all()
    count = 0
    updated = 0
    
    # Mapping helper for raw strings to standardized keys
    raw_map = {
        'not_yet_recruiting': 'not yet recruiting',
        'active_not_recruiting': 'active, not recruiting',
        'active not recruiting': 'active, not recruiting',
        'enrolling_by_invitation': 'enrolling by invitation',
    }

    for trial in trials:
        raw_status = (trial.overall_status or '').lower()
        if not raw_status:
            continue
            
        # Normalize raw status
        cleaned_status = raw_map.get(raw_status, raw_status).replace('_', ' ')
        
        # Determine target status object
        target_status = status_map.get(cleaned_status)
        
        # Fallback for Title Case match
        if not target_status:
             target_status = status_map.get(cleaned_status.title().lower())
             
        if target_status:
            # Check if likely already set to avoid churn (M2M check is a bit expensive, but safe)
            # For bulk update without clearing, we can just add.
            trial.status.add(target_status)
            updated += 1
        else:
            print(f"Warning: Could not map status '{trial.overall_status}' for trial {trial.unique_protocol_id}")

        count += 1
        if count % 100 == 0:
            print(f"Processed {count} trials...")

    print(f"\nFinished! Processed {count} trials. Added status relations.")

if __name__ == '__main__':
    seed_statuses()
