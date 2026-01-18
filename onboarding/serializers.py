from enum import Enum
from typing import OrderedDict
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .models import *



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




class MemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfile
        fields = ['profession', 'skills', 'interests', 'linkedin_url']


class InvestorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorProfile
        fields = ['investor_type', 'investment_range', 'focus_sectors', 
                  'previous_investments', 'portfolio_size']


class StartupProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupProfile
        fields = ['company_name', 'company_website', 'founded_year', 'industry',
                  'stage', 'team_size', 'funding_stage', 'product_description',
                  'target_market', 'revenue_model', 'current_revenue']


class CofounderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CofounderProfile
        fields = ['startup_name', 'role', 'equity_percentage', 'years_with_startup',
                  'expertise', 'product_description']


class IncubatorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncubatorProfile
        fields = ['organization_name', 'organization_website', 'year_established',
                  'program_type', 'startups_supported', 'support_services',
                  'success_stories', 'application_process']


class RevOpsProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevOpsProfile
        fields = ['current_company', 'current_role', 'years_experience',
                  'tools_expertise', 'specializations', 'achievements']


class CTOProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CTOProfile
        fields = ['current_company', 'current_role', 'tech_stack',
                  'team_lead_experience', 'projects_led', 'technical_expertise']


    
class UserRegistrationSerializer(serializers.Serializer):
    # Common fields
    userType = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    confirmPassword = serializers.CharField(write_only=True)
    agreeToTerms = serializers.BooleanField()
    
    # Member fields
    profession = serializers.CharField(required=False, allow_blank=True, default='')
    skills = serializers.CharField(required=False, allow_blank=True, default='')
    interests = serializers.CharField(required=False, allow_blank=True, default='')
    linkedinUrl = serializers.URLField(required=False, allow_blank=True, default='')
    
    # Investor fields
    investorType = serializers.CharField(required=False, allow_blank=True, default='')
    investmentRange = serializers.CharField(required=False, allow_blank=True, default='')
    focusSectors = serializers.CharField(required=False, allow_blank=True, default='')
    previousInvestments = serializers.CharField(required=False, allow_blank=True, default='')
    portfolioSize = serializers.CharField(required=False, allow_blank=True, default='')
    
    # Startup fields
    companyName = serializers.CharField(required=False, allow_blank=True, default='')
    companyWebsite = serializers.URLField(required=False, allow_blank=True, default='')
    foundedYear = serializers.IntegerField(required=False, allow_null=True)
    industry = serializers.CharField(required=False, allow_blank=True, default='')
    stage = serializers.CharField(required=False, allow_blank=True, default='')
    teamSize = serializers.CharField(required=False, allow_blank=True, default='')
    fundingStage = serializers.CharField(required=False, allow_blank=True, default='')
    productDescription = serializers.CharField(required=False, allow_blank=True, default='')
    targetMarket = serializers.CharField(required=False, allow_blank=True, default='')
    revenueModel = serializers.CharField(required=False, allow_blank=True, default='')
    currentRevenue = serializers.CharField(required=False, allow_blank=True, default='')
    
    # Cofounder fields
    startupName = serializers.CharField(required=False, allow_blank=True, default='')
    role = serializers.CharField(required=False, allow_blank=True, default='')
    equityPercentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    yearsWithStartup = serializers.IntegerField(required=False, allow_null=True)
    expertise = serializers.CharField(required=False, allow_blank=True, default='')
    
    # Incubator fields
    organizationName = serializers.CharField(required=False, allow_blank=True, default='')
    organizationWebsite = serializers.URLField(required=False, allow_blank=True, default='')
    yearEstablished = serializers.IntegerField(required=False, allow_null=True)
    programType = serializers.CharField(required=False, allow_blank=True, default='')
    startupsSupported = serializers.IntegerField(required=False, allow_null=True)
    successStories = serializers.CharField(required=False, allow_blank=True, default='')
    supportServices = serializers.CharField(required=False, allow_blank=True, default='')
    applicationProcess = serializers.CharField(required=False, allow_blank=True, default='')
    
    # RevOps fields
    currentCompany = serializers.CharField(required=False, allow_blank=True, default='')
    yearsExperience = serializers.CharField(required=False, allow_blank=True, default='')
    toolsExpertise = serializers.CharField(required=False, allow_blank=True, default='')
    specializations = serializers.CharField(required=False, allow_blank=True, default='')
    achievements = serializers.CharField(required=False, allow_blank=True, default='')
    
    # CTO fields
    currentRole = serializers.CharField(required=False, allow_blank=True, default='')
    techStack = serializers.CharField(required=False, allow_blank=True, default='')
    teamLeadExperience = serializers.CharField(required=False, allow_blank=True, default='')
    projectsLed = serializers.CharField(required=False, allow_blank=True, default='')
    technicalExpertise = serializers.CharField(required=False, allow_blank=True, default='')
    
    timestamp = serializers.DateTimeField(required=False)
    
    def to_internal_value(self, data):
        """Convert empty strings to None for integer/decimal fields"""
        integer_fields = ['foundedYear', 'yearsWithStartup', 'yearEstablished', 'startupsSupported']
        decimal_fields = ['equityPercentage']
        
        for field in integer_fields + decimal_fields:
            if field in data and data[field] == '':
                data[field] = None
                
        return super().to_internal_value(data)

    def validate(self, data):
        """Validate the data"""
        if data.get('password') != data.get('confirmPassword'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        if not data.get('agreeToTerms'):
            raise serializers.ValidationError({"agreeToTerms": "You must agree to the terms and conditions."})
        
        # Check if email already exists
        from .models import User
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email address already exists."})
        
        return data


























