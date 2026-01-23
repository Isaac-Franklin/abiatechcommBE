
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django.contrib.auth.models import User
# from drf_yasg.utils import swagger_auto_schema

# from onboarding.utils import resolve_user_profile, serialize_profile
# from .serializers import *
# from django.contrib.auth import authenticate
# from rest_framework.permissions import IsAuthenticated
# from django.contrib.auth import login, logout, authenticate
# from datetime import date
# from django.contrib.auth.hashers import check_password, make_password
# from rest_framework import status
# from django.db.models import Q
# from drf_yasg import openapi
# from django.views.decorators.csrf import csrf_exempt
# import socket
# import traceback
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.decorators import api_view, permission_classes, parser_classes

# from django.http import JsonResponse
# from django.views.decorators.http import require_http_methods
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import UserRegistrationSerializer
# import json

# from rest_framework_simplejwt.tokens import RefreshToken



# @swagger_auto_schema(
#     method='POST',
#     query_serializer=UserRegistrationSerializer,
#     tags=['AUTH'],
# )
# @csrf_exempt
# @api_view(['POST'])
# @require_http_methods(["POST"])
# def UserRegister(request):
#     """
#     Simple function-based view without Django Rest Framework
#     """
#     try:
#         print('request.body')
#         print(request.body)
#         data = json.loads(request.body)
#         serializer = UserRegistrationSerializer(data=data)
        
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
            
#             # Use transaction to ensure all-or-nothing save
#             with transaction.atomic():
#                 # Extract common fields
#                 user_type = validated_data.get('userType')
#                 password = validated_data.get('password')
#                 full_name = validated_data.get('name')
#                 email = validated_data.get('email')
#                 phone = validated_data.get('phone', '')
                
#                 # Split name
#                 name_parts = full_name.split(' ', 1)
#                 first_name = name_parts[0]
#                 last_name = name_parts[1] if len(name_parts) > 1 else ''
                
#                 # Create user
#                 user = User.objects.create_user(
#                     username=email,
#                     email=email,
#                     password=password,
#                     first_name=first_name,
#                     last_name=last_name,
#                 )
                
#                 # Create profile based on user type
#                 if user_type == 'member':
#                     MemberProfile.objects.create(
#                         user=user,
#                         profession=validated_data.get('profession', ''),
#                         skills=validated_data.get('skills', ''),
#                         interests=validated_data.get('interests', ''),
#                         linkedin_url=validated_data.get('linkedinUrl', ''),
#                         phone=validated_data.get('phone', ''),
#                     )
                
#                 elif user_type == 'investor':
#                     InvestorProfile.objects.create(
#                         user=user,
#                         investor_type=validated_data.get('investorType', ''),
#                         investment_range=validated_data.get('investmentRange', ''),
#                         focus_sectors=validated_data.get('focusSectors', ''),
#                         previous_investments=validated_data.get('previousInvestments', ''),
#                         portfolio_size=validated_data.get('portfolioSize', '')
#                     )
                
#                 elif user_type == 'startup':
#                     StartupProfile.objects.create(
#                         user=user,
#                         company_name=validated_data.get('companyName', ''),
#                         company_website=validated_data.get('companyWebsite', ''),
#                         founded_year=validated_data.get('foundedYear') or 2024,
#                         industry=validated_data.get('industry', ''),
#                         stage=validated_data.get('stage', ''),
#                         team_size=validated_data.get('teamSize', ''),
#                         funding_stage=validated_data.get('fundingStage', ''),
#                         product_description=validated_data.get('productDescription', ''),
#                         target_market=validated_data.get('targetMarket', ''),
#                         revenue_model=validated_data.get('revenueModel', ''),
#                         current_revenue=validated_data.get('currentRevenue', '')
#                     )
                
#                 elif user_type == 'cofounder':
#                     CofounderProfile.objects.create(
#                         user=user,
#                         startup_name=validated_data.get('startupName', ''),
#                         role=validated_data.get('role', ''),
#                         equity_percentage=validated_data.get('equityPercentage'),
#                         years_with_startup=validated_data.get('yearsWithStartup') or 0,
#                         expertise=validated_data.get('expertise', ''),
#                         product_description=validated_data.get('productDescription', '')
#                     )
                
#                 elif user_type == 'incubator':
#                     IncubatorProfile.objects.create(
#                         user=user,
#                         organization_name=validated_data.get('organizationName', ''),
#                         organization_website=validated_data.get('organizationWebsite', ''),
#                         year_established=validated_data.get('yearEstablished') or 2024,
#                         program_type=validated_data.get('programType', ''),
#                         startups_supported=validated_data.get('startupsSupported') or 0,
#                         support_services=validated_data.get('supportServices', ''),
#                         success_stories=validated_data.get('successStories', ''),
#                         application_process=validated_data.get('applicationProcess', '')
#                     )
                
#                 elif user_type == 'revops':
#                     RevOpsProfile.objects.create(
#                         user=user,
#                         current_company=validated_data.get('currentCompany', ''),
#                         current_role=validated_data.get('currentRole', ''),
#                         years_experience=validated_data.get('yearsExperience', ''),
#                         tools_expertise=validated_data.get('toolsExpertise', ''),
#                         specializations=validated_data.get('specializations', ''),
#                         achievements=validated_data.get('achievements', '')
#                     )
                
#                 elif user_type == 'cto':
#                     CTOProfile.objects.create(
#                         user=user,
#                         current_company=validated_data.get('currentCompany', ''),
#                         current_role=validated_data.get('currentRole', ''),
#                         tech_stack=validated_data.get('techStack', ''),
#                         team_lead_experience=validated_data.get('teamLeadExperience', ''),
#                         projects_led=validated_data.get('projectsLed', ''),
#                         technical_expertise=validated_data.get('technicalExpertise', '')
#                     )
            
#             # Return success response
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Registration successful!',
#                 'data': {
#                     'user_id': user.id,
#                     'email': user.email,
#                     'user_type': user_type,
#                     'name': f"{user.first_name} {user.last_name}".strip()
#                 }
#             }, status=201)
        
#         # Return validation errors
#         return JsonResponse({
#             'success': False,
#             'errors': serializer.errors
#         }, status=400)
    
#     except json.JSONDecodeError:
#         return JsonResponse({
#             'success': False,
#             'message': 'Invalid JSON data'
#         }, status=400)
    
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'message': str(e)
#         }, status=500)





# @swagger_auto_schema(
#     method='post',
#     request_body=LoginSerializer,
#     tags=['AUTH'],
#     responses={
#         200: "Login successful",
#         400: "Invalid request",
#         401: "Invalid credentials",
#     }
# )
# @csrf_exempt
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def UserLogin(request):
#     serializer = LoginSerializer(data=request.data)
#     print(request.data)

#     if not serializer.is_valid():
#         return Response(
#             {"message": "Invalid request data", "errors": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     email = serializer.validated_data['email']
#     password = serializer.validated_data['password']

#     try:
#         user = User.objects.get(email__iexact=email)
#     except User.DoesNotExist:
#         # Prevent user enumeration
#         return Response(
#             {"message": "Invalid email or password"},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     user_auth = authenticate(
#         request,
#         username=user.username,
#         password=password
#     )

#     if not user_auth:
#         return Response(
#             {"message": "Invalid email or password"},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     # 🔍 Determine user type
#     user_type, profile = resolve_user_profile(user)

#     if not profile:
#         return Response(
#             {"message": "User profile not found"},
#             status=status.HTTP_403_FORBIDDEN
#         )

#     # 🔐 Generate JWT
#     refresh = RefreshToken.for_user(user)

#     response_data = {
#         "status": 200,
#         "message": "Login successful",
#         "user_type": user_type,
#         "token": {
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#         },
#         "user": {
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email": user.email,
#         },
#         "profile": serialize_profile(profile),
#     }

#     return Response(response_data, status=status.HTTP_200_OK)



















