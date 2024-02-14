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

@router.get("/", tags=["Trials"])  # This might just be "/", based on your desired path
def get_trials(request):
    update_data()  # Update the database records first
    trials = get_serialized_trials()
    return trials
