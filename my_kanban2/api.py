from ninja import NinjaAPI

from thisapp.api.profile import router as profile_router

api_v1 = NinjaAPI(csrf=True, urls_namespace='api_v1')

api_v1.add_router('profile/', profile_router, tags=['profile'])
