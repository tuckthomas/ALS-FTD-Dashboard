from ninja import NinjaAPI, Redoc
from Dashboard.api import router as trials_router
from Dashboard.api_analytics import router as analytics_router


api = NinjaAPI(title='ALS/FTD Research Dashboard API', version='1.0.0', docs=Redoc())

api.add_router("/trials/", trials_router)
api.add_router("/analytics/", analytics_router)

