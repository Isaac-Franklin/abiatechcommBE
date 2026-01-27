from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.utils.timezone import now
from leaderboard.models import PointTransaction
from groups import models
from startups.models import Startup, StartupProfile, StartupContact
from onboarding.models import InvestorProfile   
from marketplace.models import Service, ServiceReview, ServiceContact
from datetime import timedelta
from django.utils import timezone
from jobs.models import Job
# Serializers — add ServiceSerializer and ServiceReviewSerializer here (api.serializers used above)
from .serializers import (
    LeaderboardResponseSerializer,
    PointTransactionSerializer,
    StartupSerializer,
    StartupProfileSerializer,
    StartupContactSerializer,
    ServiceSerializer,
    ServiceReviewSerializer,
    ServiceContactSerializer,
    StartupStatsSerializer,  
)
# Create your views here.
# ==================== STARTUPS ====================
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
    methods=['GET'],
    responses=StartupProfileSerializer,
    tags=['Startup User']
)
@api_view(['GET'])
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
    total_funding = Startup.objects.aggregate(models.Sum('total_funding'))['total_funding__sum'] or 0
    active_investors = InvestorProfile.objects.filter(is_active=True).count()
    jobs_created = Job.objects.count()
    # Monthly Growth
    one_month_ago = timezone.now() - timedelta(days=30)
    startups_last_month = Startup.objects.filter(created_at__gte=one_month_ago).count
    funding_last_month = Startup.objects.filter(
        last_funding_date__gte=one_month_ago
    ).aggregate(models.Sum('total_funding'))['total_funding__sum'] or 0
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
    
    # Build query
    users = PointTransaction.objects.values(
        'user__id',
        'user__first_name',
        'user__last_name',
        'user__avatar'
    ).annotate(
        total_points=models.Sum('points')
    ).order_by('-total_points')[:limit]
    
    # Build results
    results = []
    current_user_rank = None
    
    for rank, user in enumerate(users, start=1):
        is_current = user['user__id'] == request.user.id
        if is_current:
            current_user_rank = rank
            
        results.append({
            'rank': rank,
            'user': {
                'id': user['user__id'],
                'full_name': f"{user['user__first_name']} {user['user__last_name']}",
                'avatar': user.get('user__avatar')
            },
            'total_points': user['total_points'],
            'is_current_user': is_current
        })
    
    # Get total users
    total_users = PointTransaction.objects.values('user__id').distinct().count()
    
    response_data = {
        'results': results,
        'current_user_rank': current_user_rank,
        'total_users': total_users,
        'period': period
    }
    
    serializer = LeaderboardResponseSerializer(response_data)
    return Response(serializer.data)