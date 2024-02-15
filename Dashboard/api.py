from ninja import Router
from ninja.errors import ValidationError
from django.shortcuts import get_object_or_404
from .models import Trial, Gene
from .schemas import get_serialized_trials
from .utils import update_data
import pandas as pd
import os 
from django.conf import settings


router = Router()

# More of a placeholder for now, until the front-end is developed.
# Or, until I issue an SSL certificate on my reverse proxy server. If I do so before front-end development.
@router.get("/", tags=["Trials"])
def get_trials(request):
    update_data()  # Update the database records first
    trials = get_serialized_trials()
    return trials
