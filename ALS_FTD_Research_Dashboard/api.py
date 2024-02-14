from ninja import NinjaAPI
from Dashboard.api import router as trials_router

api = NinjaAPI(title='ALS/FTD Research Dashboard API', version='0.0.1')
api.add_router("/trials", trials_router)
