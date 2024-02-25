from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import jwt
import os
import time
from pathlib import Path
from django.shortcuts import render, redirect


# Metabase DashboardEmbedding
# Note: If serving this from your home server, this will require a reverse-proxy server
# Free domain names can be obtained from https://www.duckdns.org/
def Dashboard(request):
    cache.clear()  # Clear the cache
    METABASE_SITE_URL = "https://REPLACE_WITH_YOUR_HTTPS_URL"
    METABASE_SECRET_KEY = "REPLACE_WITH_YOUR_METABASE_KEY"

    payload = {
    "resource": {"dashboard": 4},
    "params": {
        
    },
    "exp": round(time.time()) + (60 * 10) # 10 minute expiration
    }
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

    iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#theme=transparent&bordered=true&titled=true"

    return render(request, 'Dashboard.html', {'iframeUrl': iframeUrl})


