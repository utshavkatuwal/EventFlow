from fastapi import APIRouter
from app.api.v1.auth_router import api_router as auth_router
from app.api.v1.events_router import api_router as events_router
from app.api.v1.events_create_router import api_router as events_create_router
from app.api.v1.categories_router import api_router as categories_router
from app.api.v1.user_router import api_router as user_router
from app.api.v1.tickets_router import api_router as tickets_router
from app.api.v1.reviews_router import api_router as reviews_router
from app.api.v1.notifications_router import api_router as notifications_router
from app.api.v1.search_router import api_router as search_router
from app.api.v1.admin_router import api_router as admin_router
from app.api.v1.organizers_router import api_router as organizers_router
from app.api.v1.users_router import api_router as users_router
from app.api.v1.user_profile_router import api_router as user_profile_router
from app.api.v1.organizer_profile_router import api_router as organizer_profile_router
from app.api.v1.organizer_applications_router import api_router as organizer_applications_router
from app.api.v1.registrations_router import api_router as registrations_router
from app.api.v1.payments_router import api_router as payments_router
from app.api.v1.organizer_ops_router import api_router as organizer_ops_router
from app.api.v1.withdrawals_router import api_router as withdrawals_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(events_router)
api_router.include_router(events_create_router)
api_router.include_router(categories_router)
api_router.include_router(user_router)
api_router.include_router(user_profile_router)
api_router.include_router(tickets_router)
api_router.include_router(reviews_router)
api_router.include_router(notifications_router)
api_router.include_router(search_router)
api_router.include_router(admin_router)
api_router.include_router(organizers_router)
api_router.include_router(users_router)
api_router.include_router(organizer_profile_router)
api_router.include_router(organizer_applications_router)
api_router.include_router(registrations_router)
api_router.include_router(payments_router)
api_router.include_router(organizer_ops_router)
api_router.include_router(withdrawals_router)
