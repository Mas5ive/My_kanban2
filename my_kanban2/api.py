from ninja import NinjaAPI

from thisapp.api.boards import router as boards_router
from thisapp.api.membership import router as membership_router

api_v1 = NinjaAPI(csrf=True, urls_namespace='api_v1')

api_v1.add_router('/', boards_router)
api_v1.add_router('/', membership_router)
