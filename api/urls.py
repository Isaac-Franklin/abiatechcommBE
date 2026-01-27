# api/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views
from api2 import views as api2_views

urlpatterns = [
    # ==================== AUTHENTICATION ====================
    path('register/', views.UserRegister, name='register'),
    path('login/', views.UserLogin, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # ==================== DASHBOARD & STATS ====================
    path('dashboard/', views.dashboard_stats, name='dashboard'),
    path('activity/recent/', views.recent_activities, name='recent-activities'),
    path('events/upcoming/', views.upcoming_events, name='upcoming-events'),
    
    # ==================== POSTS ====================
    path('posts/add/', views.add_post, name='add-post'),
    path('posts/<int:post_id>/', api2_views.get_post, name='get-post'),
    path('posts/<int:post_id>/like/', views.like_post, name='like-post'),
    path('posts/<int:post_id>/unlike/', views.unlike_post, name='unlike-post'),
    path('posts/<int:post_id>/comments/', views.get_post_comments, name='get-post-comments'),
    path('posts/<int:post_id>/comments/add/', views.create_comment, name='create-comment'),
    
    # ==================== LEARNING ====================
    # Courses
    path('learning/courses/', views.available_courses, name='available-courses'),
    path('learning/courses/enrolled/', views.enrolled_courses, name='enrolled-courses'),
    path('learning/courses/<int:course_id>/enroll/', views.enroll_course, name='enroll-course'),
    path('learning/courses/<int:course_id>/progress/', views.course_progress, name='course-progress'),
    path('learning/courses/<int:course_id>/progress/update/', views.update_progress, name='update-progress'),
    
    # Certificates
    path('learning/certificates/', views.my_certificates, name='my-certificates'),
    
    # Study Groups
    path('learning/study-groups/', views.my_study_groups, name='my-study-groups'),
    
    # Challenges
    path('learning/challenges/', views.active_challenges, name='active-challenges'),
    path('learning/challenges/<int:challenge_id>/join/', views.join_challenge, name='join-challenge'),
    
    # ==================== USER PROFILES ====================
    path('users/profile/', views.get_user_profile, name='get-user-profile'),
    path('users/profile/update/', views.update_user_profile, name='update-user-profile'),
    path('users/profile/avatar/', views.update_avatar, name='update-avatar'),
    path('users/profile/skills/', views.get_user_skills, name='get-user-skills'),
    path('users/profile/skills/add/', views.create_skill, name='create-skill'),
    path('users/profile/skills/update/', views.update_skills, name='update-skills'),
    path('users/profile/skills/<int:skill_id>/delete/', views.delete_skill, name='delete-skill'),
    path('users/profile/certifications/', views.get_certifications, name='get-certifications'),
    path('users/profile/certifications/add/', views.create_certification, name='create-certification'),
    path('users/profile/certifications/<int:cert_id>/delete/', views.delete_certification, name='delete-certification'),
    path('users/profile/projects/', views.get_projects, name='get-projects'),
    path('users/profile/projects/add/', views.create_project, name='create-project'),
    path('users/profile/projects/<int:project_id>/update/', views.update_project, name='update-project'),
    path('users/profile/projects/<int:project_id>/delete/', views.delete_project, name='delete-project'),
    # ==================== GROUPS ====================
    path('groups/', views.list_groups, name='list-groups'),
    path('groups/my-groups/', views.my_groups, name='my-groups'),
    path('groups/<int:group_id>/', views.group_detail, name='group-detail'),
    path('groups/create/', views.create_group, name='create-group'),
    path('groups/<int:group_id>/join/', views.join_group, name='join-group'),
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave-group'),
    path('groups/suggested/', views.suggested_groups, name='suggested-groups'),
    path('groups/<int:group_id>/discussions/', views.group_discussions, name='group-discussions'),
    path('groups/<int:group_id>/discussions/add/', views.create_discussion, name='create-discussion'),
    path('groups/<int:group_id>/events/', views.group_events, name='group-events'),
    path('groups/<int:group_id>/events/add/', views.create_event, name='create-event'),
    path('groups/<int:group_id>/chat/messages/', views.group_chat_messages, name='group-chat-messages'),
    path('groups/<int:group_id>/chat/messages/add/', views.create_group_chat_message, name='send-group-chat-message'),
    
    # ==================== JOBS ====================
    path('jobs/', views.list_jobs, name='list-jobs'),
    path('jobs/<int:job_id>/', views.job_detail, name='job-detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply-job'),
    path('jobs/applications/', views.my_applications, name='my-applications'),
    path('jobs/applications/<int:application_id>/', views.get_application_detail, name='get-application-detail'),
    path('jobs/bookmarked/', views.get_bookmarked_jobs, name='get-bookmarked-jobs'),
    path('jobs/<int:job_id>/bookmark/', views.toggle_job_bookmark, name='toggle-job-bookmark'),
    path('jobs/bookmarked/list/', views.bookmarked_jobs, name='bookmarked-jobs'),
    # ==================== USER SETTINGS ====================
    path('users/settings/profile/', views.update_profile, name='update-profile'),
    path('users/settings/notifications/', views.update_notifications, name='update-notifications'),
    path('users/settings/privacy/', views.update_privacy, name='update-privacy'),
    path('users/settings/change-password/', views.change_password, name='change-password'),
    path('users/account/', views.delete_account, name='delete-account'),
    path('users/<int:id>/achievements/', views.user_achievements, name='user-achievements'),
]