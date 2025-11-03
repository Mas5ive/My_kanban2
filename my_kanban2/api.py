from ninja import NinjaAPI

from thisapp.api.boards import router as boards_router

api_v1 = NinjaAPI(csrf=True, urls_namespace='api_v1')

api_v1.add_router('/', boards_router)
