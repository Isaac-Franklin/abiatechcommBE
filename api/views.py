from rest_framework.decorators import api_view, permission_classes, APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from onboarding.utils import resolve_user_profile, serialize_profile
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login, logout, authenticate
from datetime import date
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from django.db.models import Q
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
import socket
import traceback
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from startups.models import Startup, StartupContact,StartupProfile
from onboarding.models import(
    MemberProfile,IncubatorProfile, InvestorProfile,CofounderProfile,
    CTOProfile,RevOpsProfile,UserProfile,Skill,Certification
)
from leaderboard.models import UserActivityStats,UserSettings,Achievement
from learn.models import ChallengeParticipant,Certificate,Challenge,CourseEnrollment,Course,StudyGroup
from groups.models import Group, GroupChatMessage, GroupEvent, GroupDiscussion,GroupMember
from jobs.models import Job,JobApplication,JobBookmark
from django.utils.timezone import now
from django.contrib.auth import get_user_model, update_session_auth_hash
from .filters import CustomPageNumberPagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    NotificationSettingsSerializer,DashboardStatsSerializer,
    StartupProfileSerializer,AchievementSerializer,PrivacySettingsSerializer,PasswordChangeSerializer,
    ChallengeSerializer,ServiceSerializer, ServiceContactSerializer,ServiceReviewSerializer,
    CourseSerializer, CertificateSerializer,StartupSerializer,StartupContactSerializer,
    PostSerializer,PostShareSerializer,PostCommentSerializer,LoginSerializer,
    UserRegistrationSerializer,PostLikeSerializer,PostListSerializer,JobDetailSerializer,
    ActivitySerializer,GroupEventSerializer,UserProfileSerializer,JobApplicationSerializer,
    SkillSerializer,CertificationSerializer,ProjectSerializer,GroupSerializer,EnrolledCourseSerializer,
    GroupChatMessageSerializer,GroupDiscussionSerializer,GroupMemberSerializer,JobListSerializer,StudyGroupSerializer
)
from marketplace.models import Service,ServiceContact,ServiceReview
from groups.models import GroupEvent
from community.models import Post, PostLike, PostComment, PostShare,Tag, Activity, PostTag,Project
import json

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@swagger_auto_schema(
    method='POST',
    query_serializer=UserRegistrationSerializer,
    tags=['AUTH'],
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@require_http_methods(["POST"])
def UserRegister(request):
    """
    Simple function-based view without Django Rest Framework
    """
    try:
        print('request.body')
        print(request.body)
        data = json.loads(request.body)
        serializer = UserRegistrationSerializer(data=data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            # Use transaction to ensure all-or-nothing save
            with transaction.atomic():
                # Extract common fields
                user_type = validated_data.get('userType')
                password = validated_data.get('password')
                full_name = validated_data.get('name')
                email = validated_data.get('email')
                phone = validated_data.get('phone', '')
                
                # Split name
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Create user
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                
                # Create profile based on user type
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
                        tools_expertise=validated_data.get('toolsExpertise', ''),
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
            
            # Return success response
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
        
        # Return validation errors
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
        
@swagger_auto_schema(
    method='get',
    operation_summary='List groups',
    tags=['Groups'],
)
@api_view(['GET'])
def list_groups(request):
    """List all public groups with filtering"""
    groups = Group.objects.filter(
        activity_status='active',
        is_private=False
    )
    
    # Apply filters
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if category:
        groups = groups.filter(category__iexact=category)
    
    if search:
        groups = groups.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
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

@swagger_auto_schema(
    method='post',
    request_body=LoginSerializer,
    tags=['AUTH'],
    responses={
        200: "Login successful",
        400: "Invalid request",
        401: "Invalid credentials",
    }
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def UserLogin(request):
    serializer = LoginSerializer(data=request.data)
    print(request.data)

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
        # Prevent user enumeration
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

    # 🔍 Determine user type
    user_type, profile = resolve_user_profile(user)

    if not profile:
        return Response(
            {"message": "User profile not found"},
            status=status.HTTP_403_FORBIDDEN
        )

    # 🔐 Generate JWT
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

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Dashboard Statistics",
    operation_description="Get platform statistics including active members, job openings, startups, and user points",
    responses={
        200: DashboardStatsSerializer,
        401: "Authentication credentials were not provided."
    },
    security=[{'Bearer': []}],
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    GET /api/dashboard/stats/
    Returns: Active members count, job openings count, active startups count, user points
    """
    # Calculate time ranges for change comparisons
    now = timezone.now()
    today = date.today()
    last_month = now - timedelta(days=30)
    last_week = now - timedelta(days=7)
    
    # Get active members count (users active in last 30 days)
    active_members = User.objects.filter(
        last_login__gte=last_month,
        is_active=True
    ).count()
    
    # Get active members from last month for comparison
    active_members_last = User.objects.filter(
        last_login__range=[last_month - timedelta(days=30), last_month],
        is_active=True
    ).count()
    
    # Calculate member change percentage
    if active_members_last > 0:
        members_change = ((active_members - active_members_last) / active_members_last) * 100
        members_change_str = f"{'+' if members_change >= 0 else ''}{members_change:.0f}%"
    else:
        members_change_str = "+0%"
    
    # Get active job openings (not expired, active)
    job_openings = Job.objects.filter(
        is_active=True
    ).filter(
        Q(deadline__gte=today) | Q(deadline__isnull=True)
    ).count()
    
    # Get job openings from last week for comparison
    job_openings_last = Job.objects.filter(
        is_active=True,
        created_at__range=[last_week - timedelta(days=7), last_week]
    ).count()
    
    # Calculate job change percentage
    if job_openings_last > 0:
        jobs_change = ((job_openings - job_openings_last) / job_openings_last) * 100
        jobs_change_str = f"{'+' if jobs_change >= 0 else ''}{jobs_change:.0f}%"
    else:
        jobs_change_str = "+0%"
    
    # Get active startups count
    active_startups = Startup.objects.filter(
        is_active=True
    ).count()
    
    # Get startups from last month for comparison
    active_startups_last = Startup.objects.filter(
        is_active=True,
        created_at__range=[last_month - timedelta(days=30), last_month]
    ).count()
    
    # Calculate startups change percentage
    if active_startups_last > 0:
        startups_change = ((active_startups - active_startups_last) / active_startups_last) * 100
        startups_change_str = f"{'+' if startups_change >= 0 else ''}{startups_change:.0f}%"
    else:
        startups_change_str = "+0%"
    
    # Get user points from leaderboard stats
    try:
        user_stats = UserActivityStats.objects.get(user=request.user)
        user_points = user_stats.total_points
        # Get points from last week for comparison
        user_points_last_week = user_stats.points_last_week or 0
        points_change = user_points - user_points_last_week
        points_change_str = f"{'+' if points_change >= 0 else ''}{points_change}"
    except UserActivityStats.DoesNotExist:
        user_points = 0
        points_change_str = "+0"
    
    data = {
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
    
    serializer = DashboardStatsSerializer(data)
    
    return Response(serializer.data)


@swagger_auto_schema(
    method='GET',
    operation_summary="Get Recent Activities",
    operation_description="Get paginated recent activities for the current user",
    manual_parameters=[
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description="Number of items per page (max: 100)",
            type=openapi.TYPE_INTEGER,
            default=10,
            maximum=100
        )
    ],
    responses={
        200: openapi.Response(
            'Activities list',
            examples={
                'application/json': {
                    "count": 150,
                    "next": "http://api.example.org/accounts/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "activity_type": "post_like",
                            "content": "Liked your post",
                            "actor": {
                                "id": 2,
                                "name": "Jane Doe",
                                "avatar": "http://example.com/avatar.jpg"
                            },
                            "target_object_id": 123,
                            "target_content_type": "post",
                            "created_at": "2024-01-23T10:30:00Z",
                            "is_read": False
                        }
                    ]
                }
            }
        ),
        401: "Authentication credentials were not provided.",
        400: openapi.Response(
            'Invalid parameters',
            examples={
                'application/json': {
                    "error": "limit parameter cannot exceed 100"
                }
            }
        )
    },
    security=[{'Bearer': []}],
    tags=['Activities']
)
@api_view(['GET'])
def recent_activities(request):
    """
    GET /api/activities/
    
    Query params:
    - page: Page number (default: 1)
    - limit: Number of items per page (default: 10, max: 100)
    
    Returns: Paginated recent activities for the current user
    """
    # Get activities for current user
    activities = Activity.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate
    paginator = CustomPageNumberPagination()
    paginated_activities = paginator.paginate_queryset(activities, request)
    
    # Serialize
    serializer = ActivitySerializer(paginated_activities, many=True, context={'request': request})
    
    # Return paginated response
    return paginator.get_paginated_response(serializer.data)

class UpcomingEventsView(APIView):
    """
    GET /api/events/upcoming/
    Query params: page, limit
    Returns: Paginated upcoming events
    """
    @swagger_auto_schema(
        operation_summary="Get Upcoming Events",
        operation_description="Get paginated list of upcoming group events",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
                default=1,
                minimum=1
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER,
                default=10,
                minimum=1
            )
        ],
        responses={
            200: openapi.Response(
                'Upcoming events',
                examples={
                    'application/json': {
                        "results": [
                            {
                                "id": 1,
                                "title": "Tech Meetup January",
                                "description": "Monthly tech community meetup",
                                "group": {
                                    "id": 5,
                                    "name": "Tech Entrepreneurs"
                                },
                                "date": "2024-02-15T18:00:00Z",
                                "location": "Co-working Space, Lagos",
                                "event_type": "meetup",
                                "organizer": {
                                    "id": 2,
                                    "name": "Jane Smith"
                                },
                                "attendees_count": 45,
                                "max_attendees": 100,
                                "is_attending": True
                            }
                        ],
                        "pagination": {
                            "current_page": 1,
                            "total_pages": 5,
                            "total_items": 48,
                            "has_next": True,
                            "has_previous": False,
                            "next_page": 2,
                            "previous_page": None
                        }
                    }
                }
            ),
            400: openapi.Response(
                'Invalid parameters',
                examples={
                    'application/json': {
                        "error": "page and limit must be positive integers"
                    }
                }
            ),
            401: "Authentication credentials were not provided."
        },
        security=[{'Bearer': []}],
        tags=['Events']
    )
    def get(self, request):
        # Get query parameters
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
        
        # Validate pagination parameters
        if page < 1 or limit < 1:
            return Response(
                {"error": "page and limit must be positive integers"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get upcoming events (events with date >= now)
        current_time = now()
        events = GroupEvent.objects.filter(date__gte=current_time)
        
        # Paginate results
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
        
        # Serialize data
        serializer = GroupEventSerializer(events_page, many=True)
        
        # Prepare response
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
@swagger_auto_schema(
    method='POST',
    operation_summary="Create Post",
    operation_description="Create a new post with optional image and tags",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['content'],
        properties={
            'content': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Post content/text",
                example="Just launched our new product! 🚀 #excitingtimes"
            ),
            'image': openapi.Schema(
                type=openapi.TYPE_FILE,
                description="Optional image file (JPG, PNG, etc.)",
                format='binary'
            ),
            'tags': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description="List of tags/categories",
                example=['startup', 'tech', 'launch']
            )
        }
    ),
    responses={
        201: openapi.Response(
            'Success',
            PostSerializer,
            examples={
                'application/json': {
                    "id": 1,
                    "content": "Just launched our new product! 🚀",
                    "author": {
                        "id": 1,
                        "name": "John Doe"
                    },
                    "image": "http://example.com/media/posts/image.jpg",
                    "tags": ["startup", "tech"],
                    "likes_count": 0,
                    "comments_count": 0,
                    "created_at": "2024-01-23T10:30:00Z"
                }
            }
        ),
        400: openapi.Response(
            'Bad Request',
            examples={
                'application/json': {
                    "error": "Content is required"
                }
            }
        ),
        401: "Authentication credentials were not provided."
    },
    security=[{'Bearer': []}],
    tags=['Posts']
)
@api_view(['POST'])
def add_post(request):
    content = request.data.get('content')
    image = request.FILES.get("image")
    tags_data = request.data.get('tags', []) 
    if not content:
        return Response(
            {'error':'Content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    post = Post.objects.create(content=content, image=image,author=request.users)
    if isinstance(tags_data, []):
        for item in tags_data:
            tag_name = item.strip.lower()
            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                PostTag.objects.create(post=post, tag=tag)
def is_startup_owner(user, startup):
    """Check if user is the owner of the startup"""
    return True
@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Startup",
    operation_description="Update startup information (only owner can update)",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="Startup ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    request_body=StartupSerializer,
    responses={
        200: openapi.Response(
            'Success',
            examples={
                'application/json': {
                    "id": 1,
                    "name": "Updated Startup Name",
                    "description": "Updated description...",
                    "logo": "http://example.com/logo.jpg",
                    "website": "https://updated.com",
                    "industry": "Technology",
                    "founded_date": "2023-01-01",
                    "team_size": 15,
                    "funding_stage": "Series A"
                }
            }
        ),
        400: openapi.Response(
            'Validation Error',
            examples={
                'application/json': {
                    "name": ["This field is required."],
                    "industry": ["Invalid choice."]
                }
            }
        ),
        401: "Authentication credentials were not provided.",
        403: openapi.Response(
            'Forbidden',
            examples={
                'application/json': {
                    "detail": "You don't have permission to update this startup."
                }
            }
        ),
        404: "Startup not found."
    },
    security=[{'Bearer': []}],
    tags=['Startups']
)
@api_view(['PATCH'])
@parser_classes([MultiPartParser, FormParser])
def update_startup(request, id):
    """Update startup information - Only owner can update"""
    startup = get_object_or_404(Startup, id=id)
    
    # Check if user is owner (you need to implement this properly)
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

# POST /api/startups/{id}/contact/ - Send inquiry to startup
@swagger_auto_schema(
    method='POST',
    operation_summary="Contact Startup",
    operation_description="Send an inquiry/message to a startup",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="Startup ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['message'],
        properties={
            'message': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Your inquiry message to the startup",
                example="I'm interested in your product and would like to learn more."
            )
        }
    ),
    responses={
        201: openapi.Response(
            'Success',
            examples={
                'application/json': {
                    "message": "Inquiry sent successfully!",
                    "contact": {
                        "id": 1,
                        "user": 1,
                        "startup": 1,
                        "message": "I'm interested...",
                        "created_at": "2024-01-23T10:30:00Z"
                    }
                }
            }
        ),
        400: openapi.Response(
            'Bad Request',
            examples={
                'application/json': {
                    "detail": "Message is required."
                }
            }
        ),
        401: "Authentication credentials were not provided.",
        403: "You do not have permission to perform this action.",
        404: "Startup not found."
    },
    security=[{'Bearer': []}],
    tags=['Startups']
)
@api_view(['POST'])
def contact_startup(request, id):
    """Send inquiry/message to a startup"""
    startup = get_object_or_404(Startup, id=id)
    
    # Check if message exists in request
    message = request.data.get('message')
    if not message:
        return Response(
            {"detail": "Message is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create contact record
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

# Additional views for StartupProfile model

# Create Startup Profile
@swagger_auto_schema(
    method='POST',
    operation_summary="Create Startup Profile",
    operation_description="Create a startup profile for founders",
    request_body=StartupProfileSerializer,
    responses={
        201: openapi.Response(
            'Success',
            StartupProfileSerializer,
            examples={
                'application/json': {
                    "id": 1,
                    "company_name": "Tech Innovations Inc.",
                    "company_website": "https://techinnovations.com",
                    "founded_year": 2023,
                    "industry": "Technology",
                    "stage": "Seed",
                    "team_size": 10,
                    "funding_stage": "Pre-seed",
                    "product_description": "AI-powered solutions...",
                    "target_market": "SMEs",
                    "revenue_model": "Subscription",
                    "current_revenue": "100000",
                    "user": 1,
                    "created_at": "2024-01-23T10:30:00Z"
                }
            }
        ),
        400: openapi.Response(
            'Bad Request',
            examples={
                'application/json': {
                    "detail": "Startup profile already exists. Use update endpoint."
                }
            }
        ),
        401: "Authentication credentials were not provided."
    },
    security=[{'Bearer': []}],
    tags=['Startup Profile']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_startup_profile(request):
    """Create a startup profile for founders"""
    # Check if profile already exists
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

@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Startup Profile",
    operation_description="Update startup profile (only profile owner can update)",
    request_body=StartupProfileSerializer,
    responses={
        200: openapi.Response(
            'Success',
            StartupProfileSerializer,
            examples={
                'application/json': {
                    "id": 1,
                    "company_name": "Updated Tech Innovations Inc.",
                    "team_size": 15,
                    "funding_stage": "Series A",
                    "updated_at": "2024-01-23T11:30:00Z"
                }
            }
        ),
        400: openapi.Response(
            'Validation Error',
            examples={
                'application/json': {
                    "team_size": ["Team size must be positive"],
                    "funding_stage": ["Invalid funding stage"]
                }
            }
        ),
        401: "Authentication credentials were not provided.",
        404: "Startup profile not found."
    },
    security=[{'Bearer': []}],
    tags=['Startup Profile']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_startup_profile(request):
    """Update startup profile - only profile owner can update"""
    profile = get_object_or_404(StartupProfile, user=request.user)
    
    serializer = StartupProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='GET',
    operation_summary="Get user profile",
    operation_description="Get authenticated user's profile information",
    responses={
        200: openapi.Response('Profile data', examples={
            'application/json': {
                "phone": "+1234567890",
                "profession": "Software Engineer",
                "user_type": "member",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe"
            }
        }),
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['User Profile']
)
@api_view(['GET'])
def get_startup_profile(request):
    """Get current user's startup profile"""
    profile = get_object_or_404(StartupProfile, user=request.user)
    serializer = StartupProfileSerializer(profile)
    return Response(serializer.data)

# List all startups (optional)
@swagger_auto_schema(
    method='GET',
    operation_summary="List All Startups",
    operation_description="Get list of all startups",
    responses={
        200: StartupSerializer(many=True),
        401: "Unauthorized"
    },
    tags=['Startups']
)
@api_view(['GET'])
def list_startups(request):
    startups = Startup.objects.all()
    serializer = StartupSerializer(startups, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Startup Details",
    operation_description="Get detailed information about a specific startup",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="Startup ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: StartupSerializer,
        404: "Startup not found"
    },
    tags=['Startups']
)
@api_view(['GET'])
def get_startup(request, id):
    startup = get_object_or_404(Startup, id=id)
    serializer = StartupSerializer(startup)
    return Response(serializer.data)

# ==================== POST LIKES ====================

@swagger_auto_schema(
    method='POST',
    operation_summary="Like/Unlike Post",
    operation_description="Toggle like on a post (like if not liked, unlike if already liked)",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="Post ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Like status', examples={
            'application/json': {
                'liked': True,
                'likes_count': 15
            }
        }),
        401: "Unauthorized",
        404: "Post not found"
    },
    security=[{'Bearer': []}],
    tags=['Posts']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Unlike Post",
    operation_description="Remove like from a post",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="Post ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Unlike status', examples={
            'application/json': {
                'liked': False,
                'likes_count': 14
            }
        }),
        401: "Unauthorized",
        404: "Post not found"
    },
    security=[{'Bearer': []}],
    tags=['Posts']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    PostLike.objects.filter(user=request.user, post=post).delete()
    
    return Response({
        'liked': False,
        'likes_count': post.likes.count()
    })

# ==================== COMMENTS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Post Comments",
    operation_description="Get paginated comments for a post",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="Post ID",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description="Comments per page",
            type=openapi.TYPE_INTEGER,
            default=20
        )
    ],
    responses={
        200: openapi.Response('Comments list', examples={
            'application/json': {
                'results': [
                    {
                        'id': 1,
                        'content': 'Great post!',
                        'author': {'id': 2, 'name': 'Jane Doe'},
                        'created_at': '2024-01-23T10:30:00Z'
                    }
                ],
                'total': 25,
                'page': 1,
                'has_next': True,
                'has_previous': False
            }
        }),
        404: "Post not found"
    },
    tags=['Posts']
)
@api_view(['GET'])
def get_post_comments(request, post_id):
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

# ==================== LEARNING ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Enrolled Courses",
    operation_description="Get courses user is enrolled in with progress",
    responses={
        200: EnrolledCourseSerializer(many=True),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Learning']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enrolled_courses(request):
    enrollments = CourseEnrollment.objects.filter(
        user=request.user
    ).order_by('-enrolled_at')
    
    serializer = EnrolledCourseSerializer(enrollments, many=True)
    return Response({'results': serializer.data})

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Available Courses",
    operation_description="Get paginated list of available courses with filters",
    manual_parameters=[
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description="Courses per page",
            type=openapi.TYPE_INTEGER,
            default=20
        ),
        openapi.Parameter(
            'level',
            openapi.IN_QUERY,
            description="Filter by difficulty level",
            type=openapi.TYPE_STRING,
            enum=['beginner', 'intermediate', 'advanced']
        ),
        openapi.Parameter(
            'category',
            openapi.IN_QUERY,
            description="Filter by category",
            type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: openapi.Response('Courses list', examples={
            'application/json': {
                'results': [
                    {
                        'id': 1,
                        'title': 'Python for Beginners',
                        'description': 'Learn Python from scratch',
                        'instructor': 'John Doe',
                        'level': 'beginner',
                        'duration': '10 hours',
                        'enrolled_count': 150
                    }
                ],
                'total': 50,
                'page': 1,
                'total_pages': 3
            }
        })
    },
    tags=['Learning']
)
@api_view(['GET'])
def available_courses(request):
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Enroll in Course",
    operation_description="Enroll authenticated user in a course",
    manual_parameters=[
        openapi.Parameter(
            'course_id',
            openapi.IN_PATH,
            description="Course ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        201: openapi.Response('Enrollment success', examples={
            'application/json': {
                'success': True,
                'message': 'Successfully enrolled in Python for Beginners',
                'enrollment_id': 1,
                'course': {
                    'id': 1,
                    'title': 'Python for Beginners',
                    'instructor': 'john_doe'
                }
            }
        }),
        400: openapi.Response('Already enrolled', examples={
            'application/json': {
                'error': 'Already enrolled in this course'
            }
        }),
        401: "Unauthorized",
        404: "Course not found"
    },
    security=[{'Bearer': []}],
    tags=['Learning']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request, course_id):
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
            'instructor': course.instructor.username
        }
    }, status=status.HTTP_201_CREATED)
    
# GET /api/learning/courses/{id}/progress/
# ==================== LEARNING - COURSE PROGRESS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Course Progress",
    operation_description="Get user's progress in a specific course",
    manual_parameters=[
        openapi.Parameter(
            'course_id',
            openapi.IN_PATH,
            description="Course ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: EnrolledCourseSerializer,
        401: "Unauthorized",
        404: "Course or enrollment not found"
    },
    security=[{'Bearer': []}],
    tags=['Learning']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(CourseEnrollment, course=course, user=request.user)
    serializer = EnrolledCourseSerializer(enrollment)
    return Response(serializer.data)

@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Course Progress",
    operation_description="Update user's progress in a course (percentage)",
    manual_parameters=[
        openapi.Parameter(
            'course_id',
            openapi.IN_PATH,
            description="Course ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['progress'],
        properties={
            'progress': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Progress percentage (0-100)",
                minimum=0,
                maximum=100,
                example=75
            )
        }
    ),
    responses={
        200: EnrolledCourseSerializer,
        400: openapi.Response('Invalid progress value', examples={
            'application/json': {
                "error": "Progress must be an integer between 0 and 100"
            }
        }),
        401: "Unauthorized",
        404: "Course or enrollment not found"
    },
    security=[{'Bearer': []}],
    tags=['Learning']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_progress(request, course_id):
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

# ==================== CERTIFICATES ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get My Certificates",
    operation_description="Get user's earned certificates",
    responses={
        200: CertificateSerializer(many=True),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Learning']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_certificates(request):
    certificates = Certificate.objects.filter(user=request.user)
    serializer = CertificateSerializer(certificates, many=True)
    return Response({'results': serializer.data})

# ==================== STUDY GROUPS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get My Study Groups",
    operation_description="Get user's study groups",
    responses={
        200: StudyGroupSerializer(many=True),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Learning']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_study_groups(request):
    study_groups = StudyGroup.objects.filter(members=request.user)
    serializer = StudyGroupSerializer(study_groups, many=True)
    return Response({'results': serializer.data})

# ==================== CHALLENGES ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Active Challenges",
    operation_description="Get list of active challenges/hackathons",
    responses={
        200: ChallengeSerializer(many=True),
        401: "Unauthorized"
    },
    tags=['Learning']
)
@api_view(['GET'])
def active_challenges(request):
    challenges = Challenge.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    for challenge in challenges:
        challenge.participants_count = challenge.participants.count()
    serializer = ChallengeSerializer(challenges, many=True, context={'request': request})
    return Response({'results': serializer.data})

@swagger_auto_schema(
    method='POST',
    operation_summary="Join Challenge",
    operation_description="Join a challenge/hackathon",
    manual_parameters=[
        openapi.Parameter(
            'challenge_id',
            openapi.IN_PATH,
            description="Challenge ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        201: openapi.Response('Joined successfully', examples={
            'application/json': {
                'success': True,
                'message': 'Successfully joined 30-Day Code Challenge',
                'participation_id': 1,
                'challenge': {
                    'id': 1,
                    'title': '30-Day Code Challenge',
                    'deadline': '2025-02-05'
                }
            }
        }),
        400: openapi.Response('Already participating', examples={
            'application/json': {
                'error': 'Already participating in this challenge'
            }
        }),
        401: "Unauthorized",
        404: "Challenge not found or expired"
    },
    security=[{'Bearer': []}],
    tags=['Learning']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_challenge(request, challenge_id):
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

# ==================== COMMENTS ====================

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Comment",
    operation_description="Create a comment on a post",
    manual_parameters=[
        openapi.Parameter(
            'post_id',
            openapi.IN_PATH,
            description="Post ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['content'],
        properties={
            'content': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Comment text"
            ),
            'parent_comment': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Parent comment ID for replies (optional)"
            )
        }
    ),
    responses={
        201: PostCommentSerializer,
        400: openapi.Response('Content required', examples={
            'application/json': {
                'error': 'Content is required'
            }
        }),
        401: "Unauthorized",
        404: "Post or parent comment not found"
    },
    security=[{'Bearer': []}],
    tags=['Posts']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
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

# ==================== USER PROFILE ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get User Profile",
    operation_description="Get user profile (works with all profile types)",
    responses={
        200: openapi.Response('Profile data', examples={
            'application/json': {
                "phone": "+1234567890",
                "profession": "Software Engineer",
                "user_type": "member",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe"
            }
        }),
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['User Profile']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
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

@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update User Profile",
    operation_description="Update user profile information",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            'profession': openapi.Schema(type=openapi.TYPE_STRING),
            'skills': openapi.Schema(type=openapi.TYPE_STRING),
            'interests': openapi.Schema(type=openapi.TYPE_STRING),
            'linkedin_url': openapi.Schema(type=openapi.TYPE_STRING),
            'phone': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Response('Updated profile'),
        400: "Validation error",
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['User Profile']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Update Avatar",
    operation_description="Upload/update user avatar",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['avatar'],
        properties={
            'avatar': openapi.Schema(
                type=openapi.TYPE_FILE,
                description="Avatar image file"
            )
        }
    ),
    responses={
        200: openapi.Response('Avatar updated', examples={
            'application/json': {
                'avatar_url': 'http://example.com/media/avatars/image.jpg'
            }
        }),
        400: openapi.Response('Avatar required', examples={
            'application/json': {
                'error': 'Avatar file is required'
            }
        }),
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['User Profile']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_avatar(request):
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

# ==================== SKILLS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get User Skills",
    operation_description="Get user's skills (for MemberProfile)",
    responses={
        200: openapi.Response('Skills list', examples={
            'application/json': {
                'skills': ['Python', 'Django', 'React']
            }
        }),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Skills']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_skills(request):
    try:
        profile = request.user.member_profile
        skills = profile.skills.split(',') if profile.skills else []
        return Response({'skills': [s.strip() for s in skills]})
    except:
        return Response({'skills': []})

@swagger_auto_schema(
    method='POST',
    operation_summary="Add Skill",
    operation_description="Add a new skill to user's profile",
    request_body=SkillSerializer,
    responses={
        201: SkillSerializer,
        400: "Validation error",
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['Skills']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_skill(request):
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'bio': '', 'location': ''}
    )
    
    serializer = SkillSerializer(data=request.data)
    if serializer.is_valid():
        skill = serializer.save(profile=user_profile)
        return Response(SkillSerializer(skill).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='PUT',
    operation_summary="Update Skills",
    operation_description="Update user's skills (comma-separated string)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['skills'],
        properties={
            'skills': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Comma-separated skills",
                example="Python, Django, React, JavaScript"
            )
        }
    ),
    responses={
        200: openapi.Response('Skills updated', examples={
            'application/json': {
                'skills': ['Python', 'Django', 'React', 'JavaScript']
            }
        }),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Skills']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_skills(request):
    try:
        profile = request.user.member_profile
        profile.skills = request.data.get('skills', '')
        profile.save()
        return Response({'skills': profile.skills.split(',') if profile.skills else []})
    except:
        return Response({'error': 'Member profile not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete Skill",
    operation_description="Delete a specific skill",
    manual_parameters=[
        openapi.Parameter(
            'skill_id',
            openapi.IN_PATH,
            description="Skill ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        204: "Skill deleted",
        401: "Unauthorized",
        404: "Skill not found"
    },
    security=[{'Bearer': []}],
    tags=['Skills']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, profile__user=request.user)
    skill.delete()
    return Response({'message': 'Skill deleted'}, status=status.HTTP_204_NO_CONTENT)

# ==================== CERTIFICATIONS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Certifications",
    operation_description="Get user's certifications",
    responses={
        200: CertificationSerializer(many=True),
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['Certifications']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_certifications(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    certifications = profile.certifications.all()
    serializer = CertificationSerializer(certifications, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='POST',
    operation_summary="Add Certification",
    operation_description="Add a new certification",
    request_body=CertificationSerializer,
    responses={
        201: CertificationSerializer,
        400: "Validation error",
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['Certifications']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_certification(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    serializer = CertificationSerializer(data=request.data, context={'profile': profile})
    
    if serializer.is_valid():
        certification = serializer.save(profile=profile)
        return Response(CertificationSerializer(certification).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete Certification",
    operation_description="Delete a certification",
    manual_parameters=[
        openapi.Parameter(
            'cert_id',
            openapi.IN_PATH,
            description="Certification ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        204: "Certification deleted",
        401: "Unauthorized",
        404: "Certification not found"
    },
    security=[{'Bearer': []}],
    tags=['Certifications']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_certification(request, cert_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    certification = get_object_or_404(Certification, id=cert_id, profile=profile)
    certification.delete()
    return Response(
        {'message': 'Certification deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )

# ==================== PROJECTS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Projects",
    operation_description="Get user's projects",
    responses={
        200: ProjectSerializer(many=True),
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['Projects']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_projects(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    projects = profile.projects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Project",
    operation_description="Create a new project",
    request_body=ProjectSerializer,
    responses={
        201: ProjectSerializer,
        400: "Validation error",
        401: "Unauthorized",
        404: "Profile not found"
    },
    security=[{'Bearer': []}],
    tags=['Projects']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    serializer = ProjectSerializer(data=request.data, context={'profile': profile})
    
    if serializer.is_valid():
        project = serializer.save()
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Project",
    operation_description="Update a project",
    manual_parameters=[
        openapi.Parameter(
            'project_id',
            openapi.IN_PATH,
            description="Project ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    request_body=ProjectSerializer,
    responses={
        200: ProjectSerializer,
        400: "Validation error",
        401: "Unauthorized",
        404: "Project not found"
    },
    security=[{'Bearer': []}],
    tags=['Projects']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_project(request, project_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    project = get_object_or_404(Project, id=project_id, profile=profile)
    
    serializer = ProjectSerializer(project, data=request.data, partial=True, context={'profile': profile})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete Project",
    operation_description="Delete a project",
    manual_parameters=[
        openapi.Parameter(
            'project_id',
            openapi.IN_PATH,
            description="Project ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        204: "Project deleted",
        401: "Unauthorized",
        404: "Project not found"
    },
    security=[{'Bearer': []}],
    tags=['Projects']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request, project_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    project = get_object_or_404(Project, id=project_id, profile=profile)
    project.delete()
    return Response(
        {'message': 'Project deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )

# ==================== GROUPS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get My Groups",
    operation_description="Get groups where user is a member",
    manual_parameters=[
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description="Items per page",
            type=openapi.TYPE_INTEGER,
            default=20
        )
    ],
    responses={
        200: GroupSerializer(many=True),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_groups(request):
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

# ==================== JOBS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get My Applications",
    operation_description="Get user's job applications",
    manual_parameters=[
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description="Items per page",
            type=openapi.TYPE_INTEGER,
            default=20
        )
    ],
    responses={
        200: JobApplicationSerializer(many=True),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Jobs']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_applications(request):
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


## ==================== JOB APPLICATIONS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Application Details",
    operation_description="Get detailed information about a specific job application",
    manual_parameters=[
        openapi.Parameter(
            'application_id',
            openapi.IN_PATH,
            description="Application ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: JobApplicationSerializer,
        401: "Unauthorized",
        403: "Not your application",
        404: "Application not found"
    },
    security=[{'Bearer': []}],
    tags=['Jobs']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, user=request.user)
    serializer = JobApplicationSerializer(application)
    return Response(serializer.data)

# ==================== JOB BOOKMARKS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Bookmarked Jobs",
    operation_description="Get all bookmarked jobs for the authenticated user",
    manual_parameters=[
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description="Items per page",
            type=openapi.TYPE_INTEGER,
            default=20
        )
    ],
    responses={
        200: openapi.Response('Bookmarked jobs', examples={
            'application/json': {
                'results': [
                    {
                        'id': 1,
                        'title': 'Senior Developer',
                        'company': 'Tech Corp',
                        'is_bookmarked': True
                    }
                ],
                'total': 5,
                'page': 1,
                'total_pages': 1,
                'total_bookmarked': 5
            }
        }),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Jobs']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookmarked_jobs(request):
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Toggle Job Bookmark",
    operation_description="Bookmark or unbookmark a job",
    manual_parameters=[
        openapi.Parameter(
            'job_id',
            openapi.IN_PATH,
            description="Job ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Bookmark toggled', examples={
            'application/json': {
                'success': True,
                'message': 'Bookmark added successfully',
                'bookmarked': True,
                'bookmark_count': 25,
                'job': {
                    'id': 1,
                    'title': 'Senior Developer',
                    'company': 'Tech Corp'
                }
            }
        }),
        400: openapi.Response('Cannot bookmark', examples={
            'application/json': {
                'error': 'Cannot bookmark expired job',
                'bookmarked': False,
                'bookmark_count': 24
            }
        }),
        401: "Unauthorized",
        404: "Job not found"
    },
    security=[{'Bearer': []}],
    tags=['Jobs']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_job_bookmark(request, job_id):
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

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Bookmarked Jobs (Simple)",
    operation_description="Get user's bookmarked jobs (simple list)",
    responses={
        200: JobListSerializer(many=True),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Jobs']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bookmarked_jobs(request):
    bookmarked_jobs = Job.objects.filter(
        bookmarks__user=request.user,
        is_active=True
    ).order_by('-bookmarks__created_at')
    
    serializer = JobListSerializer(bookmarked_jobs, many=True, context={'request': request})
    return Response(serializer.data)

# ==================== USER SETTINGS ====================

@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Profile Settings",
    operation_description="Update user profile settings",
    request_body=UserProfileSerializer,
    responses={
        200: UserProfileSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['PATCH'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def update_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Notification Settings",
    operation_description="Update user notification preferences",
    request_body=NotificationSettingsSerializer,
    responses={
        200: NotificationSettingsSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_notifications(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Privacy Settings",
    operation_description="Update user privacy preferences",
    request_body=PrivacySettingsSerializer,
    responses={
        200: PrivacySettingsSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_privacy(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    serializer = PrivacySettingsSerializer(settings, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='POST',
    operation_summary="Change Password",
    operation_description="Change user password",
    request_body=PasswordChangeSerializer,
    responses={
        200: openapi.Response('Password changed', examples={
            'application/json': {
                'message': 'Password updated successfully'
            }
        }),
        400: openapi.Response('Invalid data', examples={
            'application/json': {
                'old_password': ['Wrong password'],
                'new_password': ['Password is too common']
            }
        }),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        update_session_auth_hash(request, user)
        return Response({'message': 'Password updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete Account",
    operation_description="Soft delete user account (deactivate)",
    responses={
        200: openapi.Response('Account deleted', examples={
            'application/json': {
                'message': 'Account deleted successfully'
            }
        }),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    user.is_active = False
    user.save()
    return Response({'message': 'Account deleted successfully'})

@swagger_auto_schema(
    method='GET',
    operation_summary="Get User Achievements",
    operation_description="Get achievements earned by a user",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="User ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: AchievementSerializer(many=True),
        404: "User not found"
    },
    tags=['Achievements']
)
@api_view(['GET'])
def user_achievements(request, id):
    user = get_object_or_404(User, id=id)
    achievements = user.achievements.all()
    serializer = AchievementSerializer(achievements, many=True)
    return Response(serializer.data)

# ==================== OTHER MISSING ENDPOINTS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Suggested Groups",
    operation_description="Get suggested groups based on user's interests",
    responses={
        200: GroupSerializer(many=True),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggested_groups(request):
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

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Group Details",
    operation_description="Get detailed information about a group",
    manual_parameters=[
        openapi.Parameter(
            'group_id',
            openapi.IN_PATH,
            description="Group ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: GroupSerializer,
        401: "Unauthorized for private groups",
        403: "Not a member of private group",
        404: "Group not found"
    },
    tags=['Groups']
)
@api_view(['GET'])
def group_detail(request, group_id):
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Leave Group",
    operation_description="Leave a group you're a member of",
    manual_parameters=[
        openapi.Parameter(
            'group_id',
            openapi.IN_PATH,
            description="Group ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Left group', examples={
            'application/json': {
                'success': True,
                'message': 'Successfully left Group Name'
            }
        }),
        400: openapi.Response('Cannot leave', examples={
            'application/json': {
                'error': 'Group creator cannot leave. Transfer ownership or delete group.'
            }
        }),
        401: "Unauthorized",
        404: "Group not found or not a member"
    },
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_group(request, group_id):
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Service",
    operation_description="Create a new marketplace service",
    request_body=ServiceSerializer,
    responses={
        201: ServiceSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Marketplace']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    serializer = ServiceSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        service = serializer.save(provider=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Startup",
    operation_description="Create a new startup profile",
    request_body=StartupSerializer,
    responses={
        201: StartupSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    tags=['Startups']
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_startup(request):
    serializer = StartupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Notification Settings",
    operation_description="Update user notification preferences",
    request_body=NotificationSettingsSerializer,
    responses={
        200: NotificationSettingsSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_notifications(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@swagger_auto_schema(
    method='POST',
    operation_summary="Create Group",
    operation_description="Create a new group",
    request_body=GroupSerializer,
    responses={
        201: GroupSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    """Create a new group"""
    serializer = GroupSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        group = serializer.save(created_by=request.user)
        
        # Add creator as admin
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Join Group",
    operation_description="Join a public group",
    manual_parameters=[
        openapi.Parameter(
            'group_id',
            openapi.IN_PATH,
            description="Group ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Join success', examples={
            'application/json': {
                'success': True,
                'message': 'Successfully joined group name',
                'role': 'member'
            }
        }),
        400: "Already a member",
        401: "Unauthorized",
        403: "Private group - request invitation",
        404: "Group not found"
    },
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request, group_id):
    """Join a group"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    # Check if already a member
    if group.members.filter(user=request.user).exists():
        return Response(
            {'error': 'Already a member of this group'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if group is private
    if group.is_private:
        return Response(
            {'error': 'This is a private group. Request invitation from admin.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Join group
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

@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update Privacy Settings",
    operation_description="Update user privacy preferences",
    request_body=PrivacySettingsSerializer,
    responses={
        200: PrivacySettingsSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_privacy(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    serializer = PrivacySettingsSerializer(settings, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='POST',
    operation_summary="Change Password",
    operation_description="Change user password",
    request_body=PasswordChangeSerializer,
    responses={
        200: openapi.Response('Password changed', examples={
            'application/json': {
                'message': 'Password updated successfully'
            }
        }),
        400: openapi.Response('Invalid data', examples={
            'application/json': {
                'old_password': ['Wrong password'],
                'new_password': ['Password is too common']
            }
        }),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        update_session_auth_hash(request, user)
        return Response({'message': 'Password updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete Account",
    operation_description="Soft delete user account (deactivate)",
    responses={
        200: openapi.Response('Account deleted', examples={
            'application/json': {
                'message': 'Account deleted successfully'
            }
        }),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Settings']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    user.is_active = False
    user.save()
    return Response({'message': 'Account deleted successfully'})

@swagger_auto_schema(
    method='GET',
    operation_summary="Get User Achievements",
    operation_description="Get achievements earned by a user",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="User ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: AchievementSerializer(many=True),
        404: "User not found"
    },
    tags=['Achievements']
)
@api_view(['GET'])
def user_achievements(request, id):
    user = get_object_or_404(User, id=id)
    achievements = user.achievements.all()
    serializer = AchievementSerializer(achievements, many=True)
    return Response(serializer.data)

# ==================== OTHER MISSING ENDPOINTS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Suggested Groups",
    operation_description="Get suggested groups based on user's interests",
    responses={
        200: GroupSerializer(many=True),
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggested_groups(request):
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

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Group Details",
    operation_description="Get detailed information about a group",
    manual_parameters=[
        openapi.Parameter(
            'group_id',
            openapi.IN_PATH,
            description="Group ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: GroupSerializer,
        401: "Unauthorized for private groups",
        403: "Not a member of private group",
        404: "Group not found"
    },
    tags=['Groups']
)
@api_view(['GET'])
def group_detail(request, group_id):
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Leave Group",
    operation_description="Leave a group you're a member of",
    manual_parameters=[
        openapi.Parameter(
            'group_id',
            openapi.IN_PATH,
            description="Group ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Left group', examples={
            'application/json': {
                'success': True,
                'message': 'Successfully left Group Name'
            }
        }),
        400: openapi.Response('Cannot leave', examples={
            'application/json': {
                'error': 'Group creator cannot leave. Transfer ownership or delete group.'
            }
        }),
        401: "Unauthorized",
        404: "Group not found or not a member"
    },
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_group(request, group_id):
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Service",
    operation_description="Create a new marketplace service",
    request_body=ServiceSerializer,
    responses={
        201: ServiceSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    security=[{'Bearer': []}],
    tags=['Marketplace']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    serializer = ServiceSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        service = serializer.save(provider=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Startup",
    operation_description="Create a new startup profile",
    request_body=StartupSerializer,
    responses={
        201: StartupSerializer,
        400: "Validation error",
        401: "Unauthorized"
    },
    tags=['Startups']
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_startup(request):
    serializer = StartupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ==================== GROUPS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Group Discussions",
    operation_description="Get discussions in a group",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="Group ID", type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1),
        openapi.Parameter('limit', openapi.IN_QUERY, description="Items per page", type=openapi.TYPE_INTEGER, default=20)
    ],
    responses={200: GroupDiscussionSerializer(many=True), 401: "Unauthorized", 403: "Not a member", 404: "Group not found"},
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_discussions(request, group_id):
    """Get group discussions"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    # Check membership
    if not group.members.filter(user=request.user).exists():
        return Response({'error': 'You must be a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    # Pagination
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

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Group Discussion",
    operation_description="Create a new discussion in a group",
    manual_parameters=[openapi.Parameter('group_id', openapi.IN_PATH, description="Group ID", type=openapi.TYPE_INTEGER, required=True)],
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['content'], properties={'content': openapi.Schema(type=openapi.TYPE_STRING, description="Discussion content")}),
    responses={201: GroupDiscussionSerializer, 400: "Content is required", 401: "Unauthorized", 403: "Not a member", 404: "Group not found"},
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_discussion(request, group_id):
    """Create a discussion"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    # Check membership
    if not group.members.filter(user=request.user).exists():
        return Response({'error': 'You must be a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    content = request.data.get('content')
    if not content or not content.strip():
        return Response({'error': 'Discussion content is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    discussion = GroupDiscussion.objects.create(group=group, author=request.user, content=content.strip())
    serializer = GroupDiscussionSerializer(discussion)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Group Events",
    operation_description="Get events in a group",
    manual_parameters=[openapi.Parameter('group_id', openapi.IN_PATH, description="Group ID", type=openapi.TYPE_INTEGER, required=True)],
    responses={200: GroupEventSerializer(many=True), 401: "Unauthorized", 403: "Not a member", 404: "Group not found"},
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_events(request, group_id):
    """Get group events"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    # Check membership
    if not group.members.filter(user=request.user).exists():
        return Response({'error': 'You must be a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    events = group.events.filter(date__gte=timezone.now()).order_by('date')
    serializer = GroupEventSerializer(events, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Group Event",
    operation_description="Create a new event in a group",
    manual_parameters=[openapi.Parameter('group_id', openapi.IN_PATH, description="Group ID", type=openapi.TYPE_INTEGER, required=True)],
    request_body=GroupEventSerializer,
    responses={201: GroupEventSerializer, 400: "Validation error", 401: "Unauthorized", 403: "Not admin/moderator", 404: "Group not found"},
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request, group_id):
    """Create a group event"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    # Check if user is admin/moderator
    member = group.members.filter(user=request.user).first()
    if not member or member.role not in ['admin', 'moderator']:
        return Response({'error': 'Only group admins and moderators can create events'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = GroupEventSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save(group=group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Group Chat Messages",
    operation_description="Get chat messages in a group",
    manual_parameters=[
        openapi.Parameter('group_id', openapi.IN_PATH, description="Group ID", type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1),
        openapi.Parameter('limit', openapi.IN_QUERY, description="Items per page", type=openapi.TYPE_INTEGER, default=50)
    ],
    responses={200: GroupChatMessageSerializer(many=True), 401: "Unauthorized", 403: "Not a member", 404: "Group not found"},
    security=[{'Bearer': []}],
    tags=['Groups']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_chat_messages(request, group_id):
    """Get chat messages"""
    group = get_object_or_404(Group, id=group_id, activity_status='active')
    
    # Check membership
    if not group.members.filter(user=request.user).exists():
        return Response({'error': 'You must be a member of this group'}, status=status.HTTP_403_FORBIDDEN)
    
    # Pagination
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

# ==================== MARKETPLACE ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="List Services",
    operation_description="Get marketplace services with filters",
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1),
        openapi.Parameter('limit', openapi.IN_QUERY, description="Items per page", type=openapi.TYPE_INTEGER, default=20),
        openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category", type=openapi.TYPE_STRING),
        openapi.Parameter('search', openapi.IN_QUERY, description="Search in title/description", type=openapi.TYPE_STRING),
        openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
        openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER)
    ],
    responses={200: ServiceSerializer(many=True)},
    tags=['Marketplace']
)
@api_view(['GET'])
def list_services(request):
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

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Service Details",
    operation_description="Get detailed information about a service",
    manual_parameters=[openapi.Parameter('service_id', openapi.IN_PATH, description="Service ID", type=openapi.TYPE_INTEGER, required=True)],
    responses={200: ServiceSerializer, 404: "Service not found"},
    tags=['Marketplace']
)
@api_view(['GET'])
def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    serializer = ServiceSerializer(service, context={'request': request})
    return Response(serializer.data)

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Service Reviews",
    operation_description="Get reviews for a service",
    manual_parameters=[openapi.Parameter('service_id', openapi.IN_PATH, description="Service ID", type=openapi.TYPE_INTEGER, required=True)],
    responses={200: ServiceReviewSerializer(many=True), 404: "Service not found"},
    tags=['Marketplace']
)
@api_view(['GET'])
def service_reviews(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    reviews = service.reviews.all().order_by('-created_at')
    serializer = ServiceReviewSerializer(reviews, many=True)
    return Response({'results': serializer.data})

@swagger_auto_schema(
    method='POST',
    operation_summary="Create Service Review",
    operation_description="Add a review for a service",
    manual_parameters=[openapi.Parameter('service_id', openapi.IN_PATH, description="Service ID", type=openapi.TYPE_INTEGER, required=True)],
    request_body=ServiceReviewSerializer,
    responses={201: ServiceReviewSerializer, 400: "Already reviewed", 401: "Unauthorized", 404: "Service not found"},
    security=[{'Bearer': []}],
    tags=['Marketplace']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if ServiceReview.objects.filter(service=service, user=request.user).exists():
        return Response({'error': 'You have already reviewed this service'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ServiceReviewSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        review = serializer.save(service=service, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='POST',
    operation_summary="Contact Service Provider",
    operation_description="Send message to service provider",
    manual_parameters=[openapi.Parameter('service_id', openapi.IN_PATH, description="Service ID", type=openapi.TYPE_INTEGER, required=True)],
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['message'], properties={'message': openapi.Schema(type=openapi.TYPE_STRING, description="Your message")}),
    responses={201: "Message sent", 400: "Message required", 401: "Unauthorized", 404: "Service not found"},
    security=[{'Bearer': []}],
    tags=['Marketplace']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_service(request, service_id):
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

# ==================== JOBS ====================

@swagger_auto_schema(
    method='GET',
    operation_summary="List Jobs",
    operation_description="Get job listings with filters",
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, default=1),
        openapi.Parameter('limit', openapi.IN_QUERY, description="Items per page", type=openapi.TYPE_INTEGER, default=20),
        openapi.Parameter('job_type', openapi.IN_QUERY, description="Filter by job type", type=openapi.TYPE_STRING, enum=['full_time', 'part_time', 'contract', 'internship', 'remote']),
        openapi.Parameter('location', openapi.IN_QUERY, description="Filter by location", type=openapi.TYPE_STRING),
        openapi.Parameter('is_remote', openapi.IN_QUERY, description="Filter remote jobs", type=openapi.TYPE_BOOLEAN),
        openapi.Parameter('search', openapi.IN_QUERY, description="Search in title/company/description", type=openapi.TYPE_STRING)
    ],
    responses={200: JobListSerializer(many=True)},
    tags=['Jobs']
)
@api_view(['GET'])
def list_jobs(request):
    """Get paginated job listings with filters"""
    # Base queryset - active jobs only
    jobs = Job.objects.filter(is_active=True)
    
    # Apply filters from query params
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
    
    # Exclude expired jobs
    jobs = jobs.filter(Q(deadline__gte=timezone.now().date()) | Q(deadline__isnull=True))
    
    # Order by featured first, then by posting date
    jobs = jobs.order_by('-is_featured', '-posted_at')
    
    # Pagination
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

@swagger_auto_schema(
    method='GET',
    operation_summary="Get Job Details",
    operation_description="Get detailed information about a job",
    manual_parameters=[openapi.Parameter('job_id', openapi.IN_PATH, description="Job ID", type=openapi.TYPE_INTEGER, required=True)],
    responses={200: JobDetailSerializer, 404: "Job not found or expired"},
    tags=['Jobs']
)
@api_view(['GET'])
def job_detail(request, job_id):
    """Get full job details"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if job is expired
    if job.is_expired:
        return Response({'error': 'This job posting has expired'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = JobDetailSerializer(job, context={'request': request})
    return Response(serializer.data)

@swagger_auto_schema(
    method='POST',
    operation_summary="Apply for Job",
    operation_description="Submit job application with resume and cover letter",
    manual_parameters=[openapi.Parameter('job_id', openapi.IN_PATH, description="Job ID", type=openapi.TYPE_INTEGER, required=True)],
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['cover_letter', 'resume'], properties={
        'cover_letter': openapi.Schema(type=openapi.TYPE_STRING, description="Cover letter text"),
        'resume': openapi.Schema(type=openapi.TYPE_FILE, description="Resume file (PDF/DOC/DOCX, max 5MB)")
    }),
    responses={201: JobApplicationSerializer, 400: "Invalid data or already applied", 401: "Unauthorized", 404: "Job not found or expired"},
    security=[{'Bearer': []}],
    tags=['Jobs']
)
@api_view(['POST'])
def apply_job(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if job is expired
    if job.is_expired:
        return Response({'error': 'This job posting has expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, user=request.user).exists():
        return Response({'error': 'You have already applied for this job'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate required fields
    cover_letter = request.data.get('cover_letter')
    resume = request.FILES.get('resume')
    
    if not cover_letter or not cover_letter.strip():
        return Response({'error': 'Cover letter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not resume:
        return Response({'error': 'Resume file is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (max 5MB)
    if resume.size > 5 * 1024 * 1024:
        return Response({'error': 'Resume file must be less than 5MB'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file type
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not any(resume.name.lower().endswith(ext) for ext in valid_extensions):
        return Response({'error': 'Resume must be PDF or Word document'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create application
    application = JobApplication.objects.create(job=job, user=request.user, cover_letter=cover_letter.strip(), resume=resume)
    
    serializer = JobApplicationSerializer(application)
    
    return Response({
        'success': True,
        'message': 'Application submitted successfully',
        'application': serializer.data,
        'application_id': application.id
    }, status=status.HTTP_201_CREATED)