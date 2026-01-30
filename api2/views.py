import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.utils.timezone import now
from leaderboard.models import PointTransaction
from groups import models as group_models
from groups.models import GroupChatMessage,GroupMember, Group,GroupDiscussion,GroupEvent
from startups.models import Startup, StartupProfile, StartupContact
from onboarding.models import InvestorProfile   
from marketplace.models import Service, ServiceReview, ServiceContact
from datetime import timedelta
from django.utils import timezone
from jobs.models import Job
from accounts.permissons import IsAdminUserType
from api.serializers import GroupChatMessageSerializer,PostSerializer, UserSerializer
from .serializers import (
    AdminUserSerializer,
    SuspendedUserSerializer,
    LeaderboardResponseSerializer,
    GroupChatMessageSerializer,
    AdminOverviewSerializer,
    AdminUserAnalyticsSerializer,
    PointTransactionSerializer,
    StartupSerializer,
    StartupProfileSerializer,
    StartupContactSerializer,
    ServiceSerializer,
    ServiceReviewSerializer,
    ServiceContactSerializer,
    StartupStatsSerializer,  
    AdminGetContentAnalytics,
)
from django.contrib.auth import get_user_model
from community.models import Post,PostComment,Project

# Create your views here.
# ==================== STARTUPS ====================
User = get_user_model()
def is_startup_owner(user, startup):
    """Check if user is the owner of the startup"""
    try:
        return startup.user == user
    except:
        return False
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
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='post_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses=PostSerializer,
    tags=['Community User']
)
@api_view(['GET'])
def get_post(request, post_id):
    """Get post details"""
    post = get_object_or_404(Post, id=post_id)
    serializer = PostSerializer(post, context={'request': request})
    return Response(serializer.data)
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
def update_startup_profile(request):
    """Update startup profile"""
    profile = get_object_or_404(StartupProfile, user=request.user)
    
    serializer = StartupProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    methods=['DELETE'],
    responses={
        204: OpenApiResponse(description="Startup profile deleted successfully."),
        404: OpenApiResponse(description="Profile not found")
    },
    tags=['Startup User']
)
@api_view(['DELETE'])
def delete_startup_profile(request):
    """Delete startup profile"""
    profile = get_object_or_404(StartupProfile, user=request.user)
    profile.delete()
    return Response({"detail": "Startup profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
@extend_schema(
    methods=['GET'],
    responses=StartupProfileSerializer,
    tags=['Startup User']
)
@api_view(['GET'])
def get_startup_profile(request):
    """Get startup profile of the logged-in user"""
    try:
        profile = StartupProfile.objects.get(user=request.user)
    except StartupProfile.DoesNotExist:
        return Response(
            {"detail": "Startup profile not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = StartupProfileSerializer(profile)
    return Response(serializer.data)
@extend_schema(
    methods=['DELETE'],
    parameters=[
        OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        204: OpenApiResponse(description="Startup deleted successfully."),
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Startup not found"),
    },
    tags=['Startup User']
)
@api_view(['DELETE'])
def delete_startup(request, id):
    """Delete a startup"""
    startup = get_object_or_404(Startup, id=id)

    if startup.owner != request.user:
        return Response(
            {"detail": "You don't have permission to delete this startup."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    startup.delete()
    return Response(
        {"detail": "Startup deleted successfully."},
        status=status.HTTP_204_NO_CONTENT
    )
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
@permission_classes([AllowAny])
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
    methods=['PATCH'],
    parameters=[
        OpenApiParameter(name='service_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request=ServiceSerializer,
    responses={
        200: ServiceSerializer,
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Service not found")
    },
    tags=['Investor User']
)
@api_view(['PATCH'])
def update_service(request, service_id):
    """Update a service"""
    service = get_object_or_404(Service, id=service_id)
    if service.provider != request.user:
        return Response(
            {"detail": "You don't have permission to update this service."},
            status=status.HTTP_403_FORBIDDEN
        )
    serializer = ServiceSerializer(service, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    methods=['DELETE'],
    parameters=[
        OpenApiParameter(name='service_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    responses={
        204: OpenApiResponse(description="Service deleted successfully."),
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Service not found")
    },
    tags=['Investor User']
)
@api_view(['DELETE'])
def delete_service(request, service_id):
    """Delete a service"""
    service = get_object_or_404(Service, id=service_id)
    
    if service.provider != request.user:
        return Response(
            {"detail": "You don't have permission to delete this service."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    service.delete()
    return Response(
        {"detail": "Service deleted successfully."},
        status=status.HTTP_204_NO_CONTENT
    )
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
def contact_service(request, service_id):
    """Contact service provider"""
    service = get_object_or_404(Service, id=service_id)
    
    message = request.data.get('message')
    if not message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    contact = ServiceContact.objects.create(service=service, user=request.user, message=message)
    serializer = ServiceContactSerializer(contact)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "data": serializer.data,
            'success': True,
            'message': 'Message sent successfully',
            'contact_id': contact.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20)
    ],
    responses=StartupStatsSerializer,
    tags=['Startup User','Investor User']
)
@api_view(["GET"])
def startup_stats(request):
    """
    Get startup and fundings stats
    """
    total_startups = Startup.objects.count()
    total_funding = Startup.objects.aggregate(Sum('total_funding'))['total_funding__sum'] or 0
    active_investors = InvestorProfile.objects.filter(is_active=True).count()
    jobs_created = Job.objects.count()
    # Monthly Growth
    one_month_ago = timezone.now() - timedelta(days=30)
    startups_last_month = Startup.objects.filter(created_at__gte=one_month_ago).count
    funding_last_month = Startup.objects.filter(
        last_funding_date__gte=one_month_ago
    ).aggregate(Sum('total_funding'))['total_funding__sum'] or 0
    startups_growth = (
        (startups_last_month / total_startups * 100) if total_startups > 0 else 0
    )
    funding_growth = (
        (funding_last_month / total_funding * 100) if total_funding > 0 else 0
    )
    data = {}
    data['total_startups'] = total_startups
    data['total_funding'] = f"${total_funding:,.2f}"
    data['active_investors'] = active_investors
    data['jobs_created'] = jobs_created
    data['month_growth'] = {
        'startups_growth': f"{startups_growth:.2f}%",
        'funding_growth': f"{funding_growth:.2f}%"
    }
    serializer = StartupStatsSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=10),
        OpenApiParameter(name='period', type=OpenApiTypes.STR, default='all-time',
                         description="Time period for leaderboard (e.g., all-time, monthly)")
    ],
    responses=LeaderboardResponseSerializer,
    tags=['Leaderboard']
)
@api_view(['GET'])
def leaderboard(request):
    limit = int(request.GET.get('limit', 10))
    period = request.GET.get('period', 'all-time')

    queryset = PointTransaction.objects.all()

    # Period filtering
    if period == 'weekly':
        queryset = queryset.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )
    elif period == 'monthly':
        queryset = queryset.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )

    # Aggregate points per user
    aggregated = queryset.values(
        'user__id',
        'user__first_name',
        'user__last_name',
        'user__avatar'
    ).annotate(
        total_points=Sum('points')
    ).order_by('-total_points')

    top_users = aggregated[:limit]

    results = []
    current_user_rank = None

    for rank, user in enumerate(top_users, start=1):
        is_current = (
            request.user.is_authenticated
            and user['user__id'] == request.user.id
        )

        if is_current:
            current_user_rank = rank

        results.append({
            'rank': rank,
            'user': {
                'id': user['user__id'],
                'full_name': f"{user['user__first_name']} {user['user__last_name']}",
                'avatar': user['user__avatar'],
            },
            'total_points': user['total_points'],
            'is_current_user': is_current,
        })

    # Calculate current user rank if not in top N
    if request.user.is_authenticated and current_user_rank is None:
        user_points = aggregated.filter(
            user__id=request.user.id
        ).first()

        if user_points:
            higher_count = aggregated.filter(
                total_points__gt=user_points['total_points']
            ).count()
            current_user_rank = higher_count + 1

    total_users = aggregated.count()

    response_data = {
        'results': results,
        'current_user_rank': current_user_rank,
        'total_users': total_users,
        'period': period,
    }

    serializer = LeaderboardResponseSerializer(response_data)
    return Response(serializer.data)
#==========================Admin===============================================#
@extend_schema(
    methods=['POST'],
    request=AdminUserSerializer,
    responses={
        201: AdminUserSerializer,
        400: OpenApiResponse(description="Validation error")
    },
    tags=['Admin User']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_signup(request):
    data = request.data
    serializer = AdminUserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20)
    ],
    responses=AdminUserSerializer(many=True),
    tags=['Admin User']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_signin(request):
    email = request.data.get("email")
    password = request.data.get("password")
    try:
        user = User.objects.get(email=email, user_type=User.UserType.ADMIN)
        if user.check_password(password):
            print("Password valid")
            refresh = RefreshToken.for_user(user)
            print("Token generated")
            serializer = AdminUserSerializer(user)
            print("Serializer created")
            print(user.is_admin())
            response = {
                "status": 200,
                "message": "Login successful",
                "is_admin": user.is_admin(),
                "token": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                },
                "data": serializer.data
            }
            print("Response ready")
            return Response(response, status=status.HTTP_200_OK)
        else:
            print("Invalid password")
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
    except User.DoesNotExist:
        print("Admin user not found")
        return Response(
            {"detail": "Admin user not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(e)
        return Response(
            {"detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@extend_schema(
    methods=['GET'],
    responses=AdminUserSerializer(many=True),
    tags=['Admin User']
)
@api_view(['GET'])
@permission_classes([IsAdminUserType])
def get_user_details(request, user_id):
    """Get user details by ID"""
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    return Response(serializer.data)
@extend_schema(
    methods=['PATCH'],
    responses=AdminUserSerializer(many=True),
    tags=['Admin User']
)
@api_view(['PATCH'])
@permission_classes([IsAdminUserType])
def update_user_details(request, user_id):
    """Update user details by ID"""
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    methods=['DELETE'],
    responses={
        204: OpenApiResponse(description="User deleted successfully."),
        404: OpenApiResponse(description="User not found")
    },
    tags=['Admin User']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUserType])
def delete_user(request, user_id):
    """"Delete a user by ID"""
    user = get_object_or_404(User, id=user_id)
    user.status = 'deleted' 
    user.delete()
    return Response(
        "User deleted successfully.",
        status=status.HTTP_204_NO_CONTENT
    )

@extend_schema(
    methods=['POST'],
    responses=AdminUserSerializer(many=True),
    tags=['Admin User']
)
@api_view(['POST'])
@permission_classes([IsAdminUserType])
def suspend_user(request, user_id):
    """Suspend a user by ID"""
    if request.user.id == user_id:
        return Response(
            {"detail": "You cannot suspend yourself."},
            status=status.HTTP_400_BAD_REQUEST
        )
    body = request.data.get('reason', 'No reason provided')
    serializer = SuspendedUserSerializer(data={'reason': body, 'suspended_at': now()})
    if serializer.is_valid():
        user = get_object_or_404(User, id=user_id)
        user.status = 'suspended'
        user.save()
        return Response(
            {"detail": f"User {user.email} suspended successfully."},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@extend_schema(
    methods=['POST'],
    responses=AdminUserSerializer(many=True),
    tags=['Admin User']
)
@api_view(['POST'])
@permission_classes([IsAdminUserType])
def activate_user(request, user_id):
    """Activate a suspended user by ID"""
    user = get_object_or_404(User, id=user_id)
    if user.status != 'suspended':
        return Response(
            {"detail": "User is not suspended."},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.status = 'active'
    user.save()
    return Response(
        {"detail": f"User {user.email} activated successfully."},
        status=status.HTTP_200_OK
    )
@extend_schema(
    methods=['GET'],
    responses=AdminUserSerializer(many=True),
    tags=['Admin User']
)
@api_view(['GET'])
@permission_classes([IsAdminUserType])
def export_users(request):
    if not request.user.is_admin():
        return Response(
            {"detail": "You don't have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    user_type =  request.data.get('user_type')
    is_active = request.data.get('is_active')
    users =[]
    if user_type:
        users = User.objects.filter(user_type=user_type)
    elif is_active:
        users = User.objects.filter(is_active=is_active)        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID','Email','Full Name','User Type','Phone','Date Joined'
    ])
    # CSV rows
    for user in users:
        writer.writerow([user.id,user.email,user.get_full_name(),user.user_type,user.phone,user.is_active,
        user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    return response
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='page', type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='limit', type=OpenApiTypes.INT, default=20),
        OpenApiParameter(name='user_type', type=OpenApiTypes.STR),
        OpenApiParameter(name='status', type=OpenApiTypes.STR),
        OpenApiParameter(name='search', type=OpenApiTypes.STR)
    ],
    responses=AdminUserSerializer(many=True),
    tags=['Admin User']
)
@api_view(['GET'])
@permission_classes([IsAdminUserType])
def user_list(request):
    """List all admin users"""
    if not request.user.is_admin():
        return Response(
            {"detail": "You don't have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    user_type= request.GET.get('user_type')
    status_filter = request.GET.get('status')
    search = request.GET.get('search')
    
    users = User.objects.all()
    #filter by user type
    if user_type:
        users = users.filter(user_type=user_type)
    #filter by status
    if status_filter:
        users = users.filter(status=status_filter)
    # Search functionality
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    pageinator = Paginator(users.order_by('-created_at'), limit)
    try:
        users_page = pageinator.page(page)
    except:
        users_page = pageinator.page(1) 
        
    serializer = UserSerializer(users_page, many=True)
    return Response({
        'results': serializer.data,
        'total': pageinator.count,
        'page': page,
        'total_pages': pageinator.num_pages
    })
@extend_schema(
    methods=['POST'],
    parameters=[
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH)
    ],
    request={
    'multipart/form-data': {
        'type': 'object',
        'properties': {
            'content': {'type': 'string'},
            'message_type': {'type': 'string', 'enum': ['text', 'file', 'image']},
            'file': {'type': 'string', 'format': 'binary'},
            'image': {'type': 'string', 'format': 'binary'}
            }
        }
    },
    responses=GroupChatMessageSerializer,
    tags=['Admin User']
)
@api_view(['POST'])
@permission_classes([IsAdminUserType])
@parser_classes([MultiPartParser,FormParser])
def admin_message_send(request, group_id):
    print(f'group is {group_id}')
    group = get_object_or_404(group_models.Group,id=group_id,activity_status= "active")
    print(f"grooup has a groi {group}")
    group_member = GroupMember.objects.filter(group=group)
    print('error')
    if not group_member.filter(user=request.user).exists():
        return Response({"detail":"You are not a member of the group"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        print("request",request.data.get('content'))
        
        content = request.data.get('content')
        message_type =request.data.get('message_type')
        file_upload = request.FILES.get("file")
        image_upload = request.FILES.get('image')
        if message_type =='text':
            if not content:
                return Response(
                    {'error':"The content is required for text message"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            message= GroupChatMessage.objects.create(
                group=group,
                user=request.user,
                message=content
            )
        elif message_type == "image":
            if not image_upload:
                return Response(
                    {"error":"The file is required"},
                    status=400
                )
            if image_upload.size > 5 * 1024 *1024:
                return Response(
                    {'error': "image size must be less 5MB"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            allowed = (".png", ".jpeg",".gif",".webp",".docx")
            if not image_upload.name.lower.endswith(allowed):
                return Response(
                    {'error':'Invalid image format, Allowed format are png, jpeg, gif, webp'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            message = GroupChatMessage.objects.create(
                group=group, 
                user=request.user,
                message=content,
                message_type=message_type,
                image= image_upload
            )
        elif message_type == 'file':
            if not file_upload:
                return Response(
                    {'error': 'File is required for file messages'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file size (10MB limit)
            if file_upload.size > 10 * 1024 * 1024:
                return Response(
                    {'error': 'File must be less than 10MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            message = GroupChatMessage.objects.create(
                group=group,
                user=request.user,
                message=content if content else file_upload.name,  # Use filename if no description
                message_type='file',
                file=file_upload
            )
        else:
            return Response(
                {'error': 'Invalid message_type. Must be: text, file, or image'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = GroupChatMessageSerializer(message, context={'request': request})
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )    
@extend_schema(
    methods=["GET"],
    parameters=[OpenApiParameter(name='page', type=OpenApiTypes.INT),
      OpenApiParameter(name="limit", type=OpenApiTypes.INT)],
     tags=['Admin User']
)    
@api_view(['GET']) 
@permission_classes([IsAdminUserType])
def admin_messages_history(request):
    messages = GroupChatMessage.objects.filter(user=request.user).order_by('-created_at')
    page = request.GET.get('page',1)
    limit= request.GET.get('limit',30)
    try:
        page= int(page)
        limit= int(limit)
    except ValueError:
        return Response(
            {"error":"page and limit must be an integer"},
            status=status.HTTP_400_BAD_REQUEST
        )
    paginator = Paginator(messages, limit)
    try:
        message_page = paginator.page(page)
    except:
        message_page= paginator.page(1)

    serializer = GroupChatMessageSerializer(message_page, many=True,context={"request":request})
    return Response(
        {
            "result":serializer.data,
            "total":paginator.count,
            "page":page,
            "total_num":paginator.num_pages
        }
    )
@extend_schema(
    methods=['GET'],
    responses=AdminOverviewSerializer,
    tags=['Admin User']
)
@api_view(['GET']) 
@permission_classes([IsAdminUserType])
def admin_overview(request):
    now = timezone.now()
    total_users = User.objects.count()
    total_content = Post.objects.count()
    new_users_7_days = User.objects.filter(created_at__gte=now-timedelta(days=7)).count()
    active_users_30_days = User.objects.filter(last_login__gte=now-timedelta(days=30)).count()
    
    overview = {}
    overview['total_users']= total_users
    overview['total_content'] = total_content
    overview["new_users_7_days"] = new_users_7_days
    overview["active_users_30_days"] = active_users_30_days
    
    serializer = AdminOverviewSerializer(overview, context={"request":request})
    return Response(serializer.data)

@extend_schema(
    methods=['GET'],
    responses=dict,
    tags=['Admin User']
)
@api_view(['GET']) 
@permission_classes([IsAdminUserType])
def admin_get_users_analytics(request):
    period = request.GET.get("period","monthly")
    now = timezone.now()
    period_mapping = {
        "daily":1,
        "weekly":7,
        "monthly":30
    }
    days = period_mapping.get(period, 30)
    data = {}
    data['period'] = period
    data['new_users'] = User.objects.filter(created_at__gte=now-timedelta(days=days)).count()
    data['active_users'] = User.objects.filter(created_at__gte=now-timedelta(days=days)).count()
    data['total_users'] = User.objects.count()
    serializer = AdminUserAnalyticsSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)
@extend_schema(
    methods=['GET'],
    responses=dict,
    tags=['Admin User']
)
@api_view(['GET']) 
@permission_classes([IsAdminUserType])
def admin_get_content_analytics(request):
    period = request.GET.get("peroid", "monthly")
    now =timezone.now()
    period_mapping= {
        "daily":1,
        "weekly":7,
        "monthly":30
    }
    days = period_mapping.get(period, 30)
    data = {}
    data['posts'] = Post.objects.filter(created_at__gte=now-timedelta(days=days))
    data['posts_comments'] = PostComment.objects.filter(created_at__gte=now-timedelta(days=days))
    data["groups"] = Group.objects.filter(created_at__gte=now-timedelta(days=days))
    data['groups_discussions']=GroupDiscussion.objects.filter(created_at__gte=now-timedelta(days=days))
    data['groups_events'] = GroupDiscussion.objects.filter(created_at__gte=now-timedelta(days=days))
    data['projects'] = Project.objects.filter(created_at__gte=now-timedelta(days=days))
    data['jobs'] = Job.objects.filter(created_at__gte=now-timedelta(days=days))
    data['startup'] = Startup.objects.filter(created_at__gte=now-timedelta(days=days))
    
    serializer = AdminGetContentAnalytics(data, many=True)
    return Response(serializer.data)