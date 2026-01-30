from django.urls import path
from . import views

urlpatterns = [
    # ==================== STARTUPS ====================
    path('startup/create/', views.create_startup, name='create-startup'),
    path('startups/list/', views.list_startups, name='list-startups'),
    path('startups/<int:id>/', views.get_startup, name='get-startup'),
    path('startups/<int:id>/update/', views.update_startup, name='update-startup'),
    path('startups/<int:id>/contact/', views.contact_startup, name='contact-startup'),
    path("startup-stats/", views.startup_stats, name="startup-stats"),
    # Startup Profile
    path('startup-profile/create/', views.create_startup_profile, name='create-startup-profile'),
    path('startup-profile/update/', views.update_startup_profile, name='update-startup-profile'),
    path('startup-profile/', views.get_startup_profile, name='get-startup-profile'),
    path('delete-startup/<int:id>/', views.delete_startup, name='delete-startup'),
    path('delete-startup-profile/<int:id>/', views.delete_startup_profile, name='delete-startup-profile'),
    path('delete-startup/<int:id>/', views.delete_startup, name='delete-startup'),

    # ==================== MARKETPLACE ====================
    path('marketplace/services/', views.list_services, name='list-services'),
    path('marketplace/services/<int:service_id>/', views.service_detail, name='service-detail'),
    path('marketplace/services/create/', views.create_service, name='create-service'),
    path('marketplace/services/<int:service_id>/reviews/', views.service_reviews, name='service-reviews'),
    path('marketplace/services/<int:service_id>/reviews/add/', views.create_review, name='create-review'),
    path('marketplace/services/<int:service_id>/contact/', views.contact_service, name='contact-service'),
    path('marketplace/services/<int:service_id>/update/', views.update_service, name='update-service'),
    path('marketplace/services/<int:service_id>/delete/', views.delete_service, name='delete-service'),
    # ==================== LEADERBOARD ====================
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    # ===================Admin===============================
    path("admin_signup/", views.admin_signup, name="admin_signup"),
    path("admin_signin/", views.admin_signin, name="admin_signin"),
    path("admin/get_user_details/<int:user_id>/", views.get_user_details, name="get_user_details"),
    path('admin/update_user_details/<int:user_id>/', views.update_user_details, name="update_user_details"),
    path('admin/delete_user/<int:user_id>/',views.delete_user, name="delete_user"),
    path('admin/suspend_user/<int:user_id>/', views.suspend_user, name="suspend_user"),
    path('admin/activate_user/<int:user_id>/',views.activate_user, name="activate_user"),
    path("admin/export_users/", views.export_users, name='export_users'),
    path('admin/user_list/', views.user_list, name='user_list'),
    path('admin/message/send/<int:group_id>/', views.admin_message_send, name="admin_message_send"),
    path('admin/message/history/', views.admin_messages_history, name="admin_message_history"),
    path('admin_overview/', views.admin_overview, name="admin_overview"),
    path('admin/analytics/users/', views.admin_get_users_analytics,name="admin_get_users_analytics"),
    path('admin/analytics/content/', views.admin_get_content_analytics, name="admin_get_analytics_content")
]