from rest_framework.decorators import api_view, permission_classes, APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Count, Q
from datetime import timedelta
from django.core.paginator import Paginator
from django.utils import timezone
from onboarding.utils import resolve_user_profile, serialize_profile
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout, authenticate
from datetime import date
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.views.decorators.csrf import csrf_exempt
import socket
import traceback
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from startups.models import Startup, StartupContact, StartupProfile
from onboarding.models import (
    MemberProfile, IncubatorProfile, InvestorProfile, CofounderProfile,
    CTOProfile, RevOpsProfile, UserProfile, Skill, Certification
)
from leaderboard.models import UserActivityStats, UserSettings, Achievement
from learn.models import ChallengeParticipant, Certificate, Challenge, CourseEnrollment, Course, StudyGroup
from groups.models import Group, GroupChatMessage, GroupEvent, GroupDiscussion, GroupMember
from jobs.models import Job, JobApplication, JobBookmark
from django.utils.timezone import now
from django.contrib.auth import get_user_model, update_session_auth_hash
from .filters import CustomPageNumberPagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from .serializers import (
    NotificationSettingsSerializer, DashboardStatsSerializer,
    StartupProfileSerializer, AchievementSerializer, PrivacySettingsSerializer, PasswordChangeSerializer,
    ChallengeSerializer, ServiceSerializer, ServiceContactSerializer, ServiceReviewSerializer,
    CourseSerializer, CertificateSerializer, StartupSerializer, StartupContactSerializer,
    PostSerializer, PostShareSerializer, PostCommentSerializer, LoginSerializer,
    UserRegistrationSerializer, PostLikeSerializer, PostListSerializer, JobDetailSerializer,
    ActivitySerializer, GroupEventSerializer, UserProfileSerializer, JobApplicationSerializer,
    SkillSerializer, CertificationSerializer, ProjectSerializer, GroupSerializer, EnrolledCourseSerializer,
    GroupChatMessageSerializer, GroupDiscussionSerializer, GroupMemberSerializer, JobListSerializer, StudyGroupSerializer
)
from marketplace.models import Service, ServiceContact, ServiceReview
from groups.models import GroupEvent
from community.models import Post, PostLike, PostComment, PostShare, Tag, Activity, PostTag, Project
import json
from functools import wraps
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Helper functions
def is_startup_owner(user, startup):
    """Check if user is the owner of the startup"""
    try:
        return startup.user == user
    except:
        return False
    
def api_wrapper(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            # log the traceback to your terminal so you can actually debug
            import traceback
            traceback.print_exc() 
            return Response({
                "success": False,
                "message": str(e)
            }, status=500)

    # Transfer ALL DRF and drf-spectacular attributes to the wrapper
    # This ensures schema generation works properly
    for attr in dir(view_func):
        if not attr.startswith('_'):
            try:
                setattr(_wrapped_view, attr, getattr(view_func, attr))
            except (AttributeError, TypeError):
                pass
    
    # Explicitly copy critical attributes that might be missed
    if hasattr(view_func, 'cls'):
        _wrapped_view.cls = view_func.cls
    if hasattr(view_func, 'schema'):
        _wrapped_view.schema = view_func.schema
    if hasattr(view_func, 'kwargs'):
        _wrapped_view.kwargs = view_func.kwargs
    if hasattr(view_func, 'actions'):
        _wrapped_view.actions = view_func.actions

    return _wrapped_view
# ==================== AUTHENTICATION ====================

@extend_schema(
    methods=['POST'],
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(
            description="Registration successful",
            response=UserRegistrationSerializer
        ),
        400: OpenApiResponse(description="Bad Request"),
        500: OpenApiResponse(description="Server Error")
    },
    tags=['Authentication'],
)
@api_view(['POST'])
@permission_classes([AllowAny])
@require_http_methods(["POST"])
@csrf_exempt
def UserRegister(request):
    """User registration endpoint"""
    try:
        data = request.data
        serializer = UserRegistrationSerializer(data=data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            with transaction.atomic():
                user_type = validated_data.get('userType')
                password = validated_data.get('password')
                full_name = validated_data.get('name')
                email = validated_data.get('email')
                phone = validated_data.get('phone', '')
                
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                
                if user_type == 'member':
                    MemberProfile.objects.create(
                        user=user,
                        profession=validated_data.get('profession', ''),
                        skills=validated_data.get('skills', ''),
                        interests=validated_data.get('interests', ''),
                        linkedin_url=validated_data.get('linkedinUrl', ''),
                        phone=validated_data.get('phone', ''),
                    )
                elif user_type == 'investor':
                    InvestorProfile.objects.create(
                        user=user,
                        investor_type=validated_data.get('investorType', ''),
                        investment_range=validated_data.get('investmentRange', ''),
                        focus_sectors=validated_data.get('focusSectors', ''),
                        previous_investments=validated_data.get('previousInvestments', ''),
                        portfolio_size=validated_data.get('portfolioSize', '')
                    )
                elif user_type == 'startup':
                    StartupProfile.objects.create(
                        user=user,
                        company_name=validated_data.get('companyName', ''),
                        company_website=validated_data.get('companyWebsite', ''),
                        founded_year=validated_data.get('foundedYear') or 2024,
                        industry=validated_data.get('industry', ''),
                        stage=validated_data.get('stage', ''),
                        team_size=validated_data.get('teamSize', ''),
                        funding_stage=validated_data.get('fundingStage', ''),
                        product_description=validated_data.get('productDescription', ''),
                        target_market=validated_data.get('targetMarket', ''),
                        revenue_model=validated_data.get('revenueModel', ''),
                        current_revenue=validated_data.get('currentRevenue', '')
                    )
                elif user_type == 'cofounder':
                    CofounderProfile.objects.create(
                        user=user,
                        startup_name=validated_data.get('startupName', ''),
                        role=validated_data.get('role', ''),
                        equity_percentage=validated_data.get('equityPercentage'),
                        years_with_startup=validated_data.get('yearsWithStartup') or 0,
                        expertise=validated_data.get('expertise', ''),
                        product_description=validated_data.get('productDescription', '')
                    )
                elif user_type == 'incubator':
                    IncubatorProfile.objects.create(
                        user=user,
                        organization_name=validated_data.get('organizationName', ''),
                        organization_website=validated_data.get('organizationWebsite', ''),
                        year_established=validated_data.get('yearEstablished') or 2024,
                        program_type=validated_data.get('programType', ''),
                        startups_supported=validated_data.get('startupsSupported') or 0,
                        support_services=validated_data.get('supportServices', ''),
                        success_stories=validated_data.get('successStories', ''),
                        application_process=validated_data.get('applicationProcess', '')
                    )
                elif user_type == 'revops':
                    RevOpsProfile.objects.create(
                        user=user,
                        current_company=validated_data.get('currentCompany', ''),
                        current_role=validated_data.get('currentRole', ''),
                        years_experience=validated_data.get('yearsExperience', ''),
                        tools_experience=validated_data.get('toolsExperience', ''),
                        specializations=validated_data.get('specializations', ''),
                        achievements=validated_data.get('achievements', '')
                    )
                elif user_type == 'cto':
                    CTOProfile.objects.create(
                        user=user,
                        current_company=validated_data.get('currentCompany', ''),
                        current_role=validated_data.get('currentRole', ''),
                        tech_stack=validated_data.get('techStack', ''),
                        team_lead_experience=validated_data.get('teamLeadExperience', ''),
                        projects_led=validated_data.get('projectsLed', ''),
                        technical_expertise=validated_data.get('technicalExpertise', '')
                    )
            
            return JsonResponse({
                'success': True,
                'message': 'Registration successful!',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'user_type': user_type,
                    'name': f"{user.first_name} {user.last_name}".strip()
                }
            }, status=201)
        
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@extend_schema(
    methods=['POST'],
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Login successful"),
        400: OpenApiResponse(description="Bad Request"),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden")
    },
    tags=['Authentication'],
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def UserLogin(request):
    """User login endpoint"""
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"message": "Invalid request data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response(
            {"message": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user_auth = authenticate(
        request,
        username=user.username,
        password=password
    )

    if not user_auth:
        return Response(
            {"message": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user_type, profile = resolve_user_profile(user)

    if not profile:
        return Response(
            {"message": "User profile not found"},
            status=status.HTTP_403_FORBIDDEN
        )

    refresh = RefreshToken.for_user(user)

    response_data = {
        "status": 200,
        "message": "Login successful",
        "user_type": user_type,
        "token": {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        },
        "profile": serialize_profile(profile),
    }

    return Response(response_data, status=status.HTTP_200_OK)

# ==================== DASHBOARD & STATS ====================

@extend_schema(
    methods=['GET'],
    responses=DashboardStatsSerializer,
    tags=['Admin User']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    now = timezone.now()
    today = date.today()
    last_month = now - timedelta(days=30)
    last_week = now - timedelta(days=7)
    
    active_members = User.objects.filter(
        last_login__gte=last_month,
        is_active=True
    ).count()
    
    active_members_last = User.objects.filter(
        last_login__range=[last_month - timedelta(days=30), last_month],
        is_active=True
    ).count()
    
    if active_members_last > 0:
        members_change = ((active_members - active_members_last) / active_members_last) * 100
        members_change_str = f"{'+' if members_change >= 0 else ''}{members_change:.0f}%"
    else:
        members_change_str = "+0%"
    
    job_openings = Job.objects.filter(
        is_active=True
    ).filter(
        Q(deadline__gte=today) | Q(deadline__isnull=True)
    ).count()
    
    job_openings_last = Job.objects.filter(
        is_active=True,
        created_at__range=[last_week - timedelta(days=7), last_week]
    ).count()
    
    if job_openings_last > 0:
        jobs_change = ((job_openings - job_openings_last) / job_openings_last) * 100
        jobs_change_str = f"{'+' if jobs_change >= 0 else ''}{jobs_change:.0f}%"
    else:
        jobs_change_str = "+0%"
    
    active_startups = Startup.objects.filter(
        is_active=True
    ).count()
    
    active_startups_last = Startup.objects.filter(
        is_active=True,
        created_at__range=[last_month - timedelta(days=30), last_month]
    ).count()
    
    if active_startups_last > 0:
        startups_change = ((active_startups - active_startups_last) / active_startups_last) * 100
        startups_change_str = f"{'+' if startups_change >= 0 else ''}{startups_change:.0f}%"
    else:
        startups_change_str = "+0%"
    
    try:
        user_stats = UserActivityStats.objects.get(user=request.user)
        user_points = user_stats.total_points
        user_points_last_week = user_stats.points_last_week or 0
        points_change = user_points - user_points_last_week
        points_change_str = f"{'+' if points_change >= 0 else ''}{points_change}"
    except UserActivityStats.DoesNotExist:
        user_points = 0
        points_change_str = "+0"
    
    dashboard_stats = {
        "active_members": active_members,
        "job_openings": job_openings,
        "active_startups": active_startups,
        "user_points": user_points,
        "changes": {
            "members_change": members_change_str,
            "jobs_change": jobs_change_str,
            "startups_change": startups_change_str,
            "points_change": points_change_str
        }
    }
    
    serializer = DashboardStatsSerializer(dashboard_stats)
    return Response(serializer.data)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=10)
    ],
    responses=ActivitySerializer(many=True),
    tags=['Admin User']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activities(request):
    """Get recent activities for current user"""
    activities = Activity.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = CustomPageNumberPagination()
    paginated_activities = paginator.paginate_queryset(activities, request)
    
    serializer = ActivitySerializer(paginated_activities, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

# Replace the entire UpcomingEventsView class with this function:

@extend_schema(
    tags=['Community User'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=10)
    ],
    responses=GroupEventSerializer(many=True),
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_events(request):
    """Get upcoming events"""
    page = request.query_params.get('page', 1)
    limit = request.query_params.get('limit', 10)
    
    try:
        page = int(page)
        limit = int(limit)
    except ValueError:
        return Response(
            {"error": "page and limit must be integers"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if page < 1 or limit < 1:
        return Response(
            {"error": "page and limit must be positive integers"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    current_time = now()
    events = GroupEvent.objects.filter(date__gte=current_time)
    
    paginator = Paginator(events, limit)
    
    try:
        events_page = paginator.page(page)
    except PageNotAnInteger:
        return Response(
            {"error": "page parameter must be an integer"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except EmptyPage:
        return Response(
            {
                "results": [],
                "pagination": {
                    "current_page": page,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "has_next": False,
                    "has_previous": paginator.num_pages > 0 and page > 1
                }
            },
            status=status.HTTP_200_OK
        )
    
    serializer = GroupEventSerializer(events_page, many=True)
    
    response_data = {
        "results": serializer.data,
        "pagination": {
            "current_page": page,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "has_next": events_page.has_next(),
            "has_previous": events_page.has_previous(),
            "next_page": events_page.next_page_number() if events_page.has_next() else None,
            "previous_page": events_page.previous_page_number() if events_page.has_previous() else None
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)
# ==================== POSTS ====================

@extend_schema(
    methods=['POST'],
    request=PostSerializer,
    responses={
        201: PostSerializer,
        400: OpenApiResponse(description="Bad Request")
    },
    tags=['Community User']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])

def add_post(request):
    """Create a new post"""
    content = request.data.get('content')
    image = request.FILES.get("image")
    tags_data = request.data.get('tags', []) 
    
    if not content:
        return Response(
            {'error':'Content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    post = Post.objects.create(content=content, image=image, author=request.user)
    
    if isinstance(tags_data, list):
        for item in tags_data:
            tag_name = item.strip().lower()
            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                PostTag.objects.create(post=post, tag=tag)
    
    serializer = PostSerializer(post)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='post_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        200: OpenApiResponse(description="Like status updated"),
        404: OpenApiResponse(description="Post not found")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    """Like or unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    
    like, created = PostLike.objects.get_or_create(
        user=request.user, 
        post=post
    )
    
    if not created:  # Unlike
        like.delete()
        liked = False
    else:  # Like
        liked = True
    
    return Response({
        'liked': liked,
        'likes_count': post.likes.count()
    })

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='post_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        200: OpenApiResponse(description="Post unliked"),
        404: OpenApiResponse(description="Post not found")
    },
    tags=['Community User']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlike_post(request, post_id):
    """Unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    
    PostLike.objects.filter(user=request.user, post=post).delete()
    
    return Response({
        'liked': False,
        'likes_count': post.likes.count()
    })

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='post_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH),
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20)
    ],
    responses=PostCommentSerializer(many=True),
    tags=['Community User']
)
@api_view(['GET'])
def get_post_comments(request, post_id):
    """Get comments for a post"""
    post = get_object_or_404(Post, id=post_id)
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    comments = PostComment.objects.filter(post=post, parent_comment=None)
    paginator = Paginator(comments, limit)
    
    try:
        comments_page = paginator.page(page)
    except:
        comments_page = paginator.page(1)
    
    serializer = PostCommentSerializer(comments_page, many=True)
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': page,
        'has_next': comments_page.has_next(),
        'has_previous': comments_page.has_previous()
    })

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='post_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=PostCommentSerializer,
    responses={
        201: PostCommentSerializer,
        400: OpenApiResponse(description="Content is required")
    },
    tags=['Community User']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    """Create a comment on a post"""
    post = get_object_or_404(Post, id=post_id)
    
    content = request.data.get('content')
    parent_comment_id = request.data.get('parent_comment')
    
    if not content:
        return Response(
            {'error': 'Content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    parent_comment = None
    if parent_comment_id:
        parent_comment = get_object_or_404(PostComment, id=parent_comment_id)
    
    comment = PostComment.objects.create(
        author=request.user,
        post=post,
        content=content,
        parent_comment=parent_comment
    )
    
    serializer = PostCommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# ==================== STARTUPS ====================

@extend_schema(
    methods=['PATCH'],
    parameters=[
        OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=StartupSerializer,
    responses={
        200: StartupSerializer,
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Startup not found")
    },
    tags=['Startup User']
)
@api_view(['PATCH'])
@parser_classes([MultiPartParser, FormParser])
def update_startup(request, id):
    """Update startup information"""
    startup = get_object_or_404(Startup, id=id)
    
    if not is_startup_owner(request.user, startup):
        return Response(
            {"detail": "You don't have permission to update this startup."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = StartupSerializer(startup, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=StartupContactSerializer,
    responses={
        201: StartupContactSerializer,
        400: OpenApiResponse(description="Message is required"),
        404: OpenApiResponse(description="Startup not found")
    },
    tags=['Startup User']
)
@api_view(['POST'])
def contact_startup(request, id):
    """Send inquiry to startup"""
    startup = get_object_or_404(Startup, id=id)
    
    message = request.data.get('message')
    if not message:
        return Response(
            {"detail": "Message is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    contact = StartupContact.objects.create(
        user=request.user,
        startup=startup,
        message=message
    )
    
    serializer = StartupContactSerializer(contact)
    
    return Response(
        {
            "message": "Inquiry sent successfully!",
            "contact": serializer.data
        },
        status=status.HTTP_201_CREATED
    )

@extend_schema(
    methods=['POST'],
    request=StartupProfileSerializer,
    responses={
        201: StartupProfileSerializer,
        400: OpenApiResponse(description="Profile already exists")
    },
    tags=['Startup User']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_startup_profile(request):
    """Create startup profile"""
    if hasattr(request.user, 'startup_profile'):
        return Response(
            {"detail": "Startup profile already exists. Use update endpoint."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = StartupProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['PATCH'],
    request=StartupProfileSerializer,
    responses={
        200: StartupProfileSerializer,
        404: OpenApiResponse(description="Profile not found")
    },
    tags=['Startup User']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_startup_profile(request):
    """Update startup profile"""
    profile = get_object_or_404(StartupProfile, user=request.user)
    
    serializer = StartupProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['GET'],
    responses=StartupProfileSerializer,
    tags=['Startup User']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_startup_profile(request):
    """Get user's startup profile"""
    profile = get_object_or_404(StartupProfile, user=request.user)
    serializer = StartupProfileSerializer(profile)
    return Response(serializer.data)

@extend_schema(
    methods=['GET'],
    responses=StartupSerializer(many=True),
    tags=['Startup User']
)
@api_view(['GET'])
def list_startups(request):
    """List all startups"""
    startups = Startup.objects.all()
    serializer = StartupSerializer(startups, many=True)
    return Response(serializer.data)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=StartupSerializer,
    tags=['Startup User']
)
@api_view(['GET'])
def get_startup(request, id):
    """Get startup details"""
    startup = get_object_or_404(Startup, id=id)
    serializer = StartupSerializer(startup)
    return Response(serializer.data)

@extend_schema(
    methods=['POST'],
    request=StartupSerializer,
    responses={
        201: StartupSerializer,
        400: OpenApiResponse(description="Validation error")
    },
    tags=['Startup User']
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_startup(request):
    """Create a new startup"""
    serializer = StartupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==================== LEARNING ====================

@extend_schema(
    methods=['GET'],
    responses=EnrolledCourseSerializer(many=True),
    tags=['Community User']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enrolled_courses(request):
    """Get enrolled courses"""
    enrollments = CourseEnrollment.objects.filter(
        user=request.user
    ).order_by('-enrolled_at')
    
    serializer = EnrolledCourseSerializer(enrollments, many=True)
    return Response({'results': serializer.data})

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20),
        OpenApiParameter(name='level', type=OpenApiTypes.STR),
        OpenApiParameter(name='category', type=OpenApiTypes.STR)
    ],
    responses=CourseSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
def available_courses(request):
    """Get available courses"""
    courses = Course.objects.all()
    
    level = request.GET.get('level')
    category = request.GET.get('category')
    
    if level:
        courses = courses.filter(level=level)
    if category:
        courses = courses.filter(category=category)
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    paginator = Paginator(courses.order_by('-id'), limit)
    
    try:
        courses_page = paginator.page(page)
    except:
        courses_page = paginator.page(1)
    
    serializer = CourseSerializer(
        courses_page, 
        many=True,
        context={'request': request}
    )
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': int(page),
        'total_pages': paginator.num_pages
    })

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='course_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        201: OpenApiResponse(description="Enrollment success"),
        400: OpenApiResponse(description="Already enrolled"),
        404: OpenApiResponse(description="Course not found")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request, course_id):
    """Enroll in a course"""
    course = get_object_or_404(Course, id=course_id)
    
    if CourseEnrollment.objects.filter(course=course, user=request.user).exists():
        return Response(
            {'error': 'Already enrolled in this course'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    enrollment = CourseEnrollment.objects.create(
        course=course,
        user=request.user,
        progress=0
    )
    
    course.enrolled_count = course.enrollments.count()
    course.save()
    
    return Response({
        'success': True,
        'message': f'Successfully enrolled in {course.title}',
        'enrollment_id': enrollment.id,
        'course': {
            'id': course.id,
            'title': course.title,
            'instructor': course.instructor.username if course.instructor else None
        }
    }, status=status.HTTP_201_CREATED)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='course_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=EnrolledCourseSerializer,
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_progress(request, course_id):
    """Get course progress"""
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(CourseEnrollment, course=course, user=request.user)
    serializer = EnrolledCourseSerializer(enrollment)
    return Response(serializer.data)

@extend_schema(
    methods=['PATCH'],
    parameters=[
        OpenApiParameter(name='course_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=OpenApiTypes.OBJECT,
    responses=EnrolledCourseSerializer,
    tags=['Community User']
)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_progress(request, course_id):
    """Update course progress"""
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(CourseEnrollment, course=course, user=request.user)
    
    progress = request.data.get('progress')
    if progress is None:
        return Response(
            {'error': 'Progress percentage is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        progress = int(progress)
        if not 0 <= progress <= 100:
            raise ValueError
    except ValueError:
        return Response(
            {'error': 'Progress must be an integer between 0 and 100'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    enrollment.progress = progress
    if progress == 100 and not enrollment.completed_at:
        enrollment.completed_at = timezone.now()
    enrollment.save()
    
    serializer = EnrolledCourseSerializer(enrollment)
    return Response(serializer.data)

@extend_schema(
    methods=['GET'],
    responses=CertificateSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_certificates(request):
    """Get user certificates"""
    certificates = Certificate.objects.filter(user=request.user)
    serializer = CertificateSerializer(certificates, many=True)
    return Response({'results': serializer.data})

@extend_schema(
    methods=['GET'],
    responses=StudyGroupSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_study_groups(request):
    """Get user's study groups"""
    study_groups = StudyGroup.objects.filter(members=request.user)
    serializer = StudyGroupSerializer(study_groups, many=True)
    return Response({'results': serializer.data})

@extend_schema(
    methods=['GET'],
    responses=ChallengeSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
def active_challenges(request):
    """Get active challenges"""
    challenges = Challenge.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    for challenge in challenges:
        challenge.participants_count = challenge.participants.count()
    serializer = ChallengeSerializer(challenges, many=True, context={'request': request})
    return Response({'results': serializer.data})

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='challenge_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        201: OpenApiResponse(description="Joined successfully"),
        400: OpenApiResponse(description="Already participating"),
        404: OpenApiResponse(description="Challenge not found")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_challenge(request, challenge_id):
    """Join a challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id, deadline__gte=timezone.now())
    
    if ChallengeParticipant.objects.filter(challenge=challenge, user=request.user).exists():
        return Response(
            {'error': 'Already participating in this challenge'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    participation = ChallengeParticipant.objects.create(challenge=challenge, user=request.user)
    
    return Response({
        'success': True,
        'message': f'Successfully joined {challenge.title}',
        'participation_id': participation.id,
        'challenge': {
            'id': challenge.id,
            'title': challenge.title,
            'deadline': challenge.deadline
        }
    }, status=status.HTTP_201_CREATED)

# ==================== USER PROFILES ====================

@extend_schema(
    methods=['GET'],
    responses=OpenApiTypes.OBJECT,
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get user profile"""
    user_type, profile = resolve_user_profile(request.user)
    
    if not profile:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    profile_data = serialize_profile(profile)
    profile_data['user_type'] = user_type
    profile_data['email'] = request.user.email
    profile_data['first_name'] = request.user.first_name
    profile_data['last_name'] = request.user.last_name
    
    return Response(profile_data)

@extend_schema(
    methods=['PATCH'],
    request=OpenApiTypes.OBJECT,
    responses=OpenApiTypes.OBJECT,
    tags=['Community User']
)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update user profile"""
    user_type, profile = resolve_user_profile(request.user)
    
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    user.save()
    
    for field, value in request.data.items():
        if field not in ['first_name', 'last_name', 'email'] and hasattr(profile, field):
            setattr(profile, field, value)
    
    profile.save()
    
    profile_data = serialize_profile(profile)
    profile_data.update({
        'user_type': user_type,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    })
    
    return Response(profile_data)

@extend_schema(
    methods=['POST'],
    request=OpenApiTypes.OBJECT,
    responses=OpenApiTypes.OBJECT,
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_avatar(request):
    """Update user avatar"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    avatar = request.FILES.get('avatar')
    if not avatar:
        return Response(
            {'error': 'Avatar file is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    profile.avatar = avatar
    profile.save()
    
    return Response({
        'avatar_url': profile.avatar.url
    })

@extend_schema(
    methods=['GET'],
    responses=OpenApiTypes.OBJECT,
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_skills(request):
    """Get user skills"""
    try:
        profile = request.user.member_profile
        skills = profile.skills.split(',') if profile.skills else []
        return Response({'skills': [s.strip() for s in skills]})
    except:
        return Response({'skills': []})

@extend_schema(
    methods=['POST'],
    request=SkillSerializer,
    responses={
        201: SkillSerializer,
        400: OpenApiResponse(description="Validation error")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_skill(request):
    """Create skill"""
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'bio': '', 'location': ''}
    )
    
    serializer = SkillSerializer(data=request.data)
    if serializer.is_valid():
        skill = serializer.save(profile=user_profile)
        return Response(SkillSerializer(skill).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['PUT'],
    request=OpenApiTypes.OBJECT,
    responses=OpenApiTypes.OBJECT,
    tags=['Community User']
)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_skills(request):
    """Update skills"""
    try:
        profile = request.user.member_profile
        profile.skills = request.data.get('skills', '')
        profile.save()
        return Response({'skills': profile.skills.split(',') if profile.skills else []})
    except:
        return Response({'error': 'Member profile not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    methods=['DELETE'],
    parameters=[
        OpenApiParameter(name='skill_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        204: OpenApiResponse(description="Skill deleted")
    },
    tags=['Community User']
)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_skill(request, skill_id):
    """Delete skill"""
    skill = get_object_or_404(Skill, id=skill_id, profile__user=request.user)
    skill.delete()
    return Response({'message': 'Skill deleted'}, status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    methods=['GET'],
    responses=CertificationSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_certifications(request):
    """Get certifications"""
    profile = get_object_or_404(UserProfile, user=request.user)
    certifications = profile.certifications.all()
    serializer = CertificationSerializer(certifications, many=True)
    return Response(serializer.data)

@extend_schema(
    methods=['POST'],
    request=CertificationSerializer,
    responses={
        201: CertificationSerializer,
        400: OpenApiResponse(description="Validation error")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_certification(request):
    """Create certification"""
    profile = get_object_or_404(UserProfile, user=request.user)
    serializer = CertificationSerializer(data=request.data, context={'profile': profile})
    
    if serializer.is_valid():
        certification = serializer.save(profile=profile)
        return Response(CertificationSerializer(certification).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['DELETE'],
    parameters=[
        OpenApiParameter(name='cert_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        204: OpenApiResponse(description="Certification deleted")
    },
    tags=['Community User']
)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_certification(request, cert_id):
    """Delete certification"""
    profile = get_object_or_404(UserProfile, user=request.user)
    certification = get_object_or_404(Certification, id=cert_id, profile=profile)
    certification.delete()
    return Response(
        {'message': 'Certification deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )

@extend_schema(
    methods=['GET'],
    responses=ProjectSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_projects(request):
    """Get projects"""
    profile = get_object_or_404(UserProfile, user=request.user)
    projects = profile.projects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@extend_schema(
    methods=['POST'],
    request=ProjectSerializer,
    responses={
        201: ProjectSerializer,
        400: OpenApiResponse(description="Validation error")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    """Create project"""
    profile = get_object_or_404(UserProfile, user=request.user)
    serializer = ProjectSerializer(data=request.data, context={'profile': profile})
    
    if serializer.is_valid():
        project = serializer.save()
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['PATCH'],
    parameters=[
        OpenApiParameter(name='project_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=ProjectSerializer,
    responses=ProjectSerializer,
    tags=['Community User']
)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_project(request, project_id):
    """Update project"""
    profile = get_object_or_404(UserProfile, user=request.user)
    project = get_object_or_404(Project, id=project_id, profile=profile)
    
    serializer = ProjectSerializer(project, data=request.data, partial=True, context={'profile': profile})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['DELETE'],
    parameters=[
        OpenApiParameter(name='project_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        204: OpenApiResponse(description="Project deleted")
    },
    tags=['Community User']
)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request, project_id):
    """Delete project"""
    profile = get_object_or_404(UserProfile, user=request.user)
    project = get_object_or_404(Project, id=project_id, profile=profile)
    project.delete()
    return Response(
        {'message': 'Project deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )

# ==================== GROUPS ====================

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20),
        OpenApiParameter(name='category', type=OpenApiTypes.STR),
        OpenApiParameter(name='search', type=OpenApiTypes.STR)
    ],
    responses=GroupSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
def list_groups(request):
    """List all public groups"""
    groups = Group.objects.filter(
        activity_status='active',
        is_private=False
    )
    
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if category:
        groups = groups.filter(category__iexact=category)
    
    if search:
        groups = groups.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    paginator = Paginator(groups.order_by('-created_at'), limit)
    
    try:
        groups_page = paginator.page(page)
    except:
        groups_page = paginator.page(1)
    
    serializer = GroupSerializer(
        groups_page, 
        many=True,
        context={'request': request}
    )
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': int(page),
        'total_pages': paginator.num_pages
    })

@extend_schema(
    methods=['GET'],
    responses=GroupSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_groups(request):
    """Get user's groups"""
    user_groups = Group.objects.filter(
        members__user=request.user,
        activity_status='active'
    ).order_by('-created_at')
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    try:
        page = int(page)
        limit = int(limit)
    except ValueError:
        return Response(
            {'error': 'page and limit must be integers'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    paginator = Paginator(user_groups, limit)
    
    try:
        groups_page = paginator.page(page)
    except:
        groups_page = paginator.page(1)
    
    serializer = GroupSerializer(groups_page, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': page,
        'total_pages': paginator.num_pages
    })

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=GroupSerializer,
    tags=['Community User']
)

@api_view(['GET'])
def group_detail(request, group_id):
    """Get group details"""
    group = get_object_or_404(Group, id=group_id)
    
    if group.is_private:
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required for private groups'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not group.members.filter(user=request.user).exists():
            return Response(
                {'error': 'Not a member of this private group'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    serializer = GroupSerializer(group, context={'request': request})
    return Response(serializer.data)

@extend_schema(
    methods=['POST'],
    request=GroupSerializer,
    responses={
        201: GroupSerializer,
        400: OpenApiResponse(description="Validation error")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    """Create a group"""
    serializer = GroupSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        group = serializer.save(created_by=request.user)
        
        GroupMember.objects.create(
            group=group,
            user=request.user,
            role='admin'
        )
        
        return Response(
            GroupSerializer(group, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        200: OpenApiResponse(description="Join success"),
        400: OpenApiResponse(description="Already a member"),
        403: OpenApiResponse(description="Private group")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request, group_id):
    """Join a group"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    if group.members.filter(user=request.user).exists():
        return Response(
            {'error': 'Already a member of this group'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if group.is_private:
        return Response(
            {'error': 'This is a private group. Request invitation from admin.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    GroupMember.objects.create(
        group=group,
        user=request.user,
        role='member'
    )
    
    return Response({
        'success': True,
        'message': f'Successfully joined {group.name}',
        'role': 'member'
    })

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        200: OpenApiResponse(description="Left group"),
        400: OpenApiResponse(description="Cannot leave")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_group(request, group_id):
    """Leave a group"""
    group = get_object_or_404(Group, id=group_id)
    member = group.members.filter(user=request.user).first()
    
    if not member:
        return Response(
            {'error': 'Not a member of this group'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if group.created_by == request.user:
        return Response(
            {'error': 'Group creator cannot leave. Transfer ownership or delete group.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    member.delete()
    return Response({
        'success': True,
        'message': f'Successfully left {group.name}'
    })

@extend_schema(
    methods=['GET'],
    responses=GroupSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggested_groups(request):
    """Get suggested groups"""
    user_categories = Group.objects.filter(
        members__user=request.user
    ).values_list('category', flat=True).distinct()
    
    suggested = Group.objects.exclude(members__user=request.user).filter(
        activity_status='active',
        is_private=False
    ).filter(Q(category__in=user_categories) if user_categories else Q()
    ).annotate(member_count=Count('members')
    ).order_by('-member_count')[:10]
    
    serializer = GroupSerializer(suggested, many=True, context={'request': request})
    return Response(serializer.data)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH),
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20)
    ],
    responses=GroupDiscussionSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_discussions(request, group_id):
    """Get group discussions"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    if not group.members.filter(user=request.user).exists():
        return Response({'error': 'You must be a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    discussions = group.discussions.all().order_by('-created_at')
    paginator = Paginator(discussions, limit)
    
    try:
        discussions_page = paginator.page(page)
    except:
        discussions_page = paginator.page(1)
    
    serializer = GroupDiscussionSerializer(discussions_page, many=True)
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': int(page),
        'total_pages': paginator.num_pages
    })

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=OpenApiTypes.OBJECT,
    responses={
        201: GroupDiscussionSerializer,
        400: OpenApiResponse(description="Content is required"),
        403: OpenApiResponse(description="Not a member")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_discussion(request, group_id):
    """Create group discussion"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    if not group.members.filter(user=request.user).exists():
        return Response({'error': 'You must be a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    content = request.data.get('content')
    if not content or not content.strip():
        return Response({'error': 'Discussion content is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    discussion = GroupDiscussion.objects.create(group=group, author=request.user, content=content.strip())
    serializer = GroupDiscussionSerializer(discussion)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=GroupEventSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_events(request, group_id):
    """Get group events"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    if not group.members.filter(user=request.user).exists():
        return Response({'error': 'You must be a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    events = group.events.filter(date__gte=timezone.now()).order_by('date')
    serializer = GroupEventSerializer(events, many=True)
    return Response(serializer.data)

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=GroupEventSerializer,
    responses={
        201: GroupEventSerializer,
        400: OpenApiResponse(description="Validation error"),
        403: OpenApiResponse(description="Not admin/moderator")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])

def create_event(request, group_id):
    """Create group event"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    member = group.members.filter(user=request.user).first()
    if not member or member.role not in ['admin', 'moderator']:
        return Response({'error': 'Only group admins and moderators can create events'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = GroupEventSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save(group=group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH),
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=50)
    ],
    responses=GroupChatMessageSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_chat_messages(request, group_id):
    """Get group chat messages"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    if not group.members.filter(user=request.user).exists():
        return Response({'error': 'You must be a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    page = request.GET.get('page', 1)
    limit = min(int(request.GET.get('limit', 50)), 100)
    
    messages = GroupChatMessage.objects.filter(group=group).order_by('-created_at')
    paginator = Paginator(messages, limit)
    
    try:
        messages_page = paginator.page(page)
    except:
        messages_page = paginator.page(1)
    
    serializer = GroupChatMessageSerializer(messages_page, many=True)
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': int(page),
        'total_pages': paginator.num_pages
    })

# ==================== JOBS ====================

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20),
        OpenApiParameter(name='job_type', type=OpenApiTypes.STR),
        OpenApiParameter(name='location', type=OpenApiTypes.STR),
        OpenApiParameter(name='is_remote', type=OpenApiTypes.BOOL),
        OpenApiParameter(name='search', type=OpenApiTypes.STR)
    ],
    responses=JobListSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
def list_jobs(request):
    """List jobs with filters"""
    jobs = Job.objects.filter(is_active=True)
    
    job_type = request.GET.get('job_type')
    location = request.GET.get('location')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    search = request.GET.get('search')
    is_remote = request.GET.get('is_remote')
    experience_level = request.GET.get('experience_level')
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if salary_min:
        try:
            jobs = jobs.filter(salary_min__gte=float(salary_min))
        except ValueError:
            pass
    
    if salary_max:
        try:
            jobs = jobs.filter(salary_max__lte=float(salary_max))
        except ValueError:
            pass
    
    if is_remote:
        jobs = jobs.filter(is_remote=(is_remote.lower() == 'true'))
    
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)
    
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(company__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__contains=[search])
        )
    
    jobs = jobs.filter(Q(deadline__gte=timezone.now().date()) | Q(deadline__isnull=True))
    jobs = jobs.order_by('-is_featured', '-posted_at')
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    try:
        page = int(page)
        limit = min(int(limit), 50)
    except ValueError:
        return Response({'error': 'page and limit must be integers'}, status=status.HTTP_400_BAD_REQUEST)
    
    paginator = Paginator(jobs, limit)
    
    try:
        jobs_page = paginator.page(page)
    except:
        jobs_page = paginator.page(1)
    
    serializer = JobListSerializer(jobs_page, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': page,
        'total_pages': paginator.num_pages,
        'filters': {
            'job_type': job_type,
            'location': location,
            'is_remote': is_remote,
            'experience_level': experience_level
        }
    })

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='job_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=JobDetailSerializer,
    tags=['Community User']
)

@api_view(['GET'])
def job_detail(request, job_id):
    """Get job details"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if job.is_expired:
        return Response({'error': 'This job posting has expired'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = JobDetailSerializer(job, context={'request': request})
    return Response(serializer.data)

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='job_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=OpenApiTypes.OBJECT,
    responses={
        201: JobApplicationSerializer,
        400: OpenApiResponse(description="Invalid data or already applied"),
        404: OpenApiResponse(description="Job not found or expired")
    },
    tags=['Community User']
)

@api_view(['POST'])
def apply_job(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if job.is_expired:
        return Response({'error': 'This job posting has expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    if JobApplication.objects.filter(job=job, user=request.user).exists():
        return Response({'error': 'You have already applied for this job'}, status=status.HTTP_400_BAD_REQUEST)
    
    cover_letter = request.data.get('cover_letter')
    resume = request.FILES.get('resume')
    
    if not cover_letter or not cover_letter.strip():
        return Response({'error': 'Cover letter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not resume:
        return Response({'error': 'Resume file is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if resume.size > 5 * 1024 * 1024:
        return Response({'error': 'Resume file must be less than 5MB'}, status=status.HTTP_400_BAD_REQUEST)
    
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not any(resume.name.lower().endswith(ext) for ext in valid_extensions):
        return Response({'error': 'Resume must be PDF or Word document'}, status=status.HTTP_400_BAD_REQUEST)
    
    application = JobApplication.objects.create(job=job, user=request.user, cover_letter=cover_letter.strip(), resume=resume)
    
    serializer = JobApplicationSerializer(application)
    
    return Response({
        'success': True,
        'message': 'Application submitted successfully',
        'application': serializer.data,
        'application_id': application.id
    }, status=status.HTTP_201_CREATED)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20)
    ],
    responses=JobApplicationSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_applications(request):
    """Get user's job applications"""
    applications = JobApplication.objects.filter(user=request.user).order_by('-applied_at')
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    paginator = Paginator(applications, limit)
    
    try:
        apps_page = paginator.page(page)
    except:
        apps_page = paginator.page(1)
    
    serializer = JobApplicationSerializer(apps_page, many=True)
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': int(page),
        'total_pages': paginator.num_pages
    })

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='application_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=JobApplicationSerializer,
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application_detail(request, application_id):
    """Get application details"""
    application = get_object_or_404(JobApplication, id=application_id, user=request.user)
    serializer = JobApplicationSerializer(application)
    return Response(serializer.data)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20)
    ],
    responses=JobListSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookmarked_jobs(request):
    """Get bookmarked jobs"""
    bookmarked_jobs = Job.objects.filter(
        bookmarks__user=request.user,
        is_active=True
    ).exclude(is_expired=True).order_by('-bookmarks__created_at')
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    paginator = Paginator(bookmarked_jobs, limit)
    
    try:
        jobs_page = paginator.page(page)
    except:
        jobs_page = paginator.page(1)
    
    serializer = JobListSerializer(jobs_page, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'total_bookmarked': paginator.count
    })

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='job_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        200: OpenApiResponse(description="Bookmark toggled"),
        400: OpenApiResponse(description="Cannot bookmark expired job"),
        404: OpenApiResponse(description="Job not found")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_job_bookmark(request, job_id):
    """Toggle job bookmark"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if job.is_expired:
        return Response(
            {
                'error': 'Cannot bookmark expired job',
                'bookmarked': False,
                'bookmark_count': job.bookmarks.count()
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    bookmark, created = JobBookmark.objects.get_or_create(user=request.user, job=job)
    
    if not created:
        bookmark.delete()
        bookmarked = False
        action = 'removed'
    else:
        bookmarked = True
        action = 'added'
    
    bookmark_count = job.bookmarks.count()
    
    return Response({
        'success': True,
        'message': f'Bookmark {action} successfully',
        'bookmarked': bookmarked,
        'bookmark_count': bookmark_count,
        'job': {
            'id': job.id,
            'title': job.title,
            'company': job.company
        }
    })

@extend_schema(
    methods=['GET'],
    responses=JobListSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bookmarked_jobs(request):
    """Get bookmarked jobs (simple list)"""
    bookmarked_jobs = Job.objects.filter(
        bookmarks__user=request.user,
        is_active=True
    ).order_by('-bookmarks__created_at')
    
    serializer = JobListSerializer(bookmarked_jobs, many=True, context={'request': request})
    return Response(serializer.data)

# ==================== MARKETPLACE ====================

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20),
        OpenApiParameter(name='category', type=OpenApiTypes.STR),
        OpenApiParameter(name='search', type=OpenApiTypes.STR),
        OpenApiParameter(name='min_price', type=OpenApiTypes.NUMBER),
        OpenApiParameter(name='max_price', type=OpenApiTypes.NUMBER)
    ],
    responses=ServiceSerializer(many=True),
    tags=['Investor User']
)

@api_view(['GET'])
def list_services(request):
    """List marketplace services"""
    services = Service.objects.all()
    
    category = request.GET.get('category')
    search = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if category:
        services = services.filter(category=category)
    
    if search:
        services = services.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    if min_price:
        try:
            services = services.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            services = services.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)
    
    paginator = Paginator(services.order_by('-created_at'), limit)
    
    try:
        services_page = paginator.page(page)
    except:
        services_page = paginator.page(1)
    
    serializer = ServiceSerializer(services_page, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': int(page),
        'total_pages': paginator.num_pages
    })

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='service_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=ServiceSerializer,
    tags=['Investor User']
)

@api_view(['GET'])
def service_detail(request, service_id):
    """Get service details"""
    service = get_object_or_404(Service, id=service_id)
    serializer = ServiceSerializer(service, context={'request': request})
    return Response(serializer.data)

@extend_schema(
    methods=['POST'],
    request=ServiceSerializer,
    responses={
        201: ServiceSerializer,
        400: OpenApiResponse(description="Validation error")
    },
    tags=['Investor User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    """Create marketplace service"""
    serializer = ServiceSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        service = serializer.save(provider=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='service_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=ServiceReviewSerializer(many=True),
    tags=['Investor User']
)

@api_view(['GET'])
def service_reviews(request, service_id):
    """Get service reviews"""
    service = get_object_or_404(Service, id=service_id)
    reviews = service.reviews.all().order_by('-created_at')
    serializer = ServiceReviewSerializer(reviews, many=True)
    return Response({'results': serializer.data})

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='service_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=ServiceReviewSerializer,
    responses={
        201: ServiceReviewSerializer,
        400: OpenApiResponse(description="Already reviewed")
    },
    tags=['Investor User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, service_id):
    """Create service review"""
    service = get_object_or_404(Service, id=service_id)
    
    if ServiceReview.objects.filter(service=service, user=request.user).exists():
        return Response({'error': 'You have already reviewed this service'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ServiceReviewSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        review = serializer.save(service=service, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='service_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=OpenApiTypes.OBJECT,
    responses={
        201: OpenApiResponse(description="Message sent"),
        400: OpenApiResponse(description="Message required")
    },
    tags=['Investor User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_service(request, service_id):
    """Contact service provider"""
    service = get_object_or_404(Service, id=service_id)
    
    message = request.data.get('message')
    if not message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    contact = ServiceContact.objects.create(service=service, user=request.user, message=message)
    
    return Response({
        'success': True,
        'message': 'Message sent successfully',
        'contact_id': contact.id
    }, status=status.HTTP_201_CREATED)

# ==================== USER SETTINGS ====================

@extend_schema(
    methods=['PATCH'],
    request=UserProfileSerializer,
    responses=UserProfileSerializer,
    tags=['Community User']
)

@api_view(['PATCH'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['PATCH'],
    request=NotificationSettingsSerializer,
    responses=NotificationSettingsSerializer,
    tags=['Community User']
)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_notifications(request):
    """Update notification settings"""
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['PATCH'],
    request=PrivacySettingsSerializer,
    responses=PrivacySettingsSerializer,
    tags=['Community User']
)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_privacy(request):
    """Update privacy settings"""
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    serializer = PrivacySettingsSerializer(settings, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['POST'],
    request=PasswordChangeSerializer,
    responses={
        200: OpenApiResponse(description="Password changed"),
        400: OpenApiResponse(description="Invalid data")
    },
    tags=['Community User']
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password"""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        update_session_auth_hash(request, user)
        return Response({'message': 'Password updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=['DELETE'],
    responses={
        200: OpenApiResponse(description="Account deleted")
    },
    tags=['Community User']
)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Delete account"""
    user = request.user
    user.is_active = False
    user.save()
    return Response({'message': 'Account deleted successfully'})

@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=AchievementSerializer(many=True),
    tags=['Community User']
)

@api_view(['GET'])
def user_achievements(request, id):
    """Get user achievements"""
    user = get_object_or_404(User, id=id)
    achievements = user.achievements.all()
    serializer = AchievementSerializer(achievements, many=True)
    return Response(serializer.data)

