from django.urls import path
from . import views

urlpatterns = [
    # ==================== STARTUPS ====================
    path('startup/create/', views.create_startup, name='create-startup'),
    path('startups/list/', views.list_startups, name='list-startups'),
    path('startups/<int:id>/', views.get_startup, name='get-startup'),
    path('startups/<int:id>/update/', views.update_startup, name='update-startup'),
    path('startups/<int:id>/contact/', views.contact_startup, name='contact-startup'),
    # Startup Profile
    path('startup-profile/create/', views.create_startup_profile, name='create-startup-profile'),
    path('startup-profile/update/', views.update_startup_profile, name='update-startup-profile'),
    path('startup-profile/', views.get_startup_profile, name='get-startup-profile'),
    
    # ==================== MARKETPLACE ====================
    path('marketplace/services/', views.list_services, name='list-services'),
    path('marketplace/services/<int:service_id>/', views.service_detail, name='service-detail'),
    path('marketplace/services/create/', views.create_service, name='create-service'),
    path('marketplace/services/<int:service_id>/reviews/', views.service_reviews, name='service-reviews'),
    path('marketplace/services/<int:service_id>/reviews/add/', views.create_review, name='create-review'),
    path('marketplace/services/<int:service_id>/contact/', views.contact_service, name='contact-service'),
]