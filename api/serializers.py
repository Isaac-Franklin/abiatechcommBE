from enum import Enum
from typing import OrderedDict
from rest_framework import serializers
from onboarding.models import (MemberProfile, RevOpsProfile, Skill, 
    UserProfile, InvestorProfile, CofounderProfile, 
    IncubatorProfile,CTOProfile,
    Certification
)
from django.utils import timezone
from startups.models import Startup,StartupProfile,StartupContact
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from groups.models import Group, GroupMember, GroupDiscussion, GroupEvent, GroupChatMessage
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from community.models import Post, PostLike, PostComment, PostShare, Activity,Tag,PostTag,Project
from groups.models import GroupEvent
from jobs.models import Job, JobApplication, JobBookmark
from django.utils.timezone import now
from learn.models import Course,Certificate,Challenge,ChallengeParticipant,CourseEnrollment,StudyGroup
from marketplace.models import Service,ServiceContact,ServiceReview
from leaderboard.models import Achievement,PointTransaction,UserActivityStats,UserSettings


User= get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields= "__all__"
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email

        return token
    
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"
 
class ServiceContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceContact
        fields = "__all__"
        
class ServiceReviewSerializer(serializers.ModelSerializer):
    class Meta :
        model = ServiceReview
        fields = "__all__"
        
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields= "__all__"
        
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

class CertificationSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)
    duration = serializers.CharField(read_only=True)
    certificate_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Certification
        fields = [
            'id', 'title', 'issuer', 'issue_date', 'expiry_date',
            'credential_id', 'credential_url', 'description',
            'is_verified', 'is_public', 'certificate_file',
            'certificate_file_url', 'is_expired', 'duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired', 'duration']
    
    def get_certificate_file_url(self, obj):
        if obj.certificate_file:
            return obj.certificate_file.url
        return None
    
    def validate_issue_date(self, value):
        """Validate issue date is not in the future"""
        if value > timezone.now().date():
            raise serializers.ValidationError("Issue date cannot be in the future")
        return value
    
    def validate_expiry_date(self, value):
        """Validate expiry date is after issue date"""
        issue_date = self.initial_data.get('issue_date')
        if issue_date and value:
            if value < issue_date:
                raise serializers.ValidationError("Expiry date must be after issue date")
        return value
    
    def validate(self, data):
        """Additional validation"""
        # Check if certification already exists for this user
        profile = self.context.get('profile')
        if profile and 'title' in data and 'issuer' in data:
            existing = Certification.objects.filter(
                profile=profile,
                title__iexact=data['title'],
                issuer__iexact=data['issuer']
            ).exists()
            if existing:
                raise serializers.ValidationError(
                    "You already have this certification"
                )
        return data
    
    def create(self, validated_data):
        profile = self.context.get('profile')
        if not profile:
            raise serializers.ValidationError("Profile is required")
        return Certification.objects.create(profile=profile, **validated_data)
    
class CofounderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CofounderProfile
        fields = ['startup_name', 'role', 'equity_percentage', 'years_with_startup',
                  'expertise', 'product_description']

class StartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = [
            'id', 'name', 'description', 'category', 'stage', 
            'team_size', 'funding', 'website', 'logo', 
            'founded_date', 'location'
        ]
        read_only_fields = ['id']

class StartupContactSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    startup_name = serializers.CharField(source='startup.name', read_only=True)
    
    class Meta:
        model = StartupContact
        fields = ['id', 'user', 'user_name', 'startup', 'startup_name', 'message', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class StartupProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = StartupProfile
        fields = [
            'id', 'user', 'user_email', 'company_name', 'company_website', 
            'founded_year', 'industry', 'stage', 'team_size', 'funding_stage',
            'product_description', 'target_market', 'revenue_model', 'current_revenue'
        ]
        read_only_fields = ['id', 'user']

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

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        
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
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email address already exists."})
        
        return data

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields="__all__"
        
class DashboardStatsSerializer(serializers.Serializer):
    active_members = serializers.IntegerField()
    job_openings = serializers.IntegerField()
    active_startups = serializers.IntegerField()
    user_points = serializers.IntegerField()
    
    class ChangesSerializer(serializers.Serializer):
        members_change = serializers.CharField()
        jobs_change = serializers.CharField()
        startups_change = serializers.CharField()
        points_change = serializers.CharField()
    
    changes = ChangesSerializer()
class PostCommentSerializer(serializers.ModelSerializer):
    """Serializer for PostComment model"""
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PostComment
        fields = [
            'id', 'author', 'author_id', 'post', 'content', 
            'parent_comment', 'replies', 'reply_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_replies(self, obj):
        """Get nested replies for this comment"""
        if obj.replies.exists():
            return PostCommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def get_reply_count(self, obj):
        """Count of replies to this comment"""
        return obj.replies.count()
    
    def create(self, validated_data):
        # Set author from context if not provided
        if 'author_id' not in validated_data:
            validated_data['author'] = self.context['request'].user
        else:
            validated_data['author_id'] = validated_data.pop('author_id')
        return super().create(validated_data)


class PostLikeSerializer(serializers.ModelSerializer):
    """Serializer for PostLike model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'user_id', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # Set user from context if not provided
        if 'user_id' not in validated_data:
            validated_data['user'] = self.context['request'].user
        else:
            validated_data['user_id'] = validated_data.pop('user_id')
        return super().create(validated_data)


        
class PostShareSerializer(serializers.ModelSerializer):
    """Serializer for PostShare model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = PostShare
        fields = ['id', 'user', 'user_id', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # Set user from context if not provided
        if 'user_id' not in validated_data:
            validated_data['user'] = self.context['request'].user
        else:
            validated_data['user_id'] = validated_data.pop('user_id')
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model"""
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    share_count = serializers.ReadOnlyField()
    comments = PostCommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_id', 'content', 'image',
            'like_count', 'comment_count', 'share_count',
            'comments', 'is_liked', 'is_shared',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        """Check if the current user has liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def get_is_shared(self, obj):
        """Check if the current user has shared this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostShare.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def create(self, validated_data):
        # Set author from context if not provided
        if 'author_id' not in validated_data:
            validated_data['author'] = self.context['request'].user
        else:
            validated_data['author_id'] = validated_data.pop('author_id')
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing posts (without nested comments)"""
    author = UserSerializer(read_only=True)
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    share_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'image',
            'like_count', 'comment_count', 'share_count',
            'is_liked', 'is_shared',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def get_is_shared(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostShare.objects.filter(user=request.user, post=obj).exists()
        return False


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model"""
    user = UserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_type_display', read_only=True)
    content_object_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = [
            'id', 'user', 'action_type', 'action_display',
            'content_type', 'object_id', 'content_object_data',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_content_object_data(self, obj):
        """Serialize the related content object"""
        content_obj = obj.content_object
        
        if isinstance(content_obj, Post):
            return {
                'type': 'post',
                'id': content_obj.id,
                'content': content_obj.content[:100],  # First 100 chars
                'author': content_obj.author.username
            }
        elif isinstance(content_obj, PostComment):
            return {
                'type': 'comment',
                'id': content_obj.id,
                'content': content_obj.content[:100],
                'post_id': content_obj.post.id
            }
        elif isinstance(content_obj, PostLike):
            return {
                'type': 'like',
                'id': content_obj.id,
                'post_id': content_obj.post.id
            }
        elif isinstance(content_obj, PostShare):
            return {
                'type': 'share',
                'id': content_obj.id,
                'post_id': content_obj.post.id
            }
        elif isinstance(content_obj, User):
            return {
                'type': 'user',
                'id': content_obj.id,
                'username': content_obj.username
            }
        
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer specifically for creating posts"""
    class Meta:
        model = Post
        fields = ['content', 'image']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer specifically for creating comments"""
    class Meta:
        model = PostComment
        fields = ['post', 'content', 'parent_comment']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class GroupEventSerializer(serializers.ModelSerializer):
    month = serializers.ReadOnlyField()
    day = serializers.ReadOnlyField()
    formatted_date = serializers.ReadOnlyField(source='formatted_date')
    
    class Meta:
        model = GroupEvent
        fields = ['id', 'title', 'location', 'formatted_date', 'month', 'day']
        read_only_fields = ['month', 'day', 'formatted_date']


class CertificationSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)
    duration = serializers.CharField(read_only=True)
    certificate_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Certification
        fields = [
            'id', 'title', 'issuer', 'issue_date', 'expiry_date',
            'credential_id', 'credential_url', 'description',
            'is_verified', 'is_public', 'certificate_file',
            'certificate_file_url', 'is_expired', 'duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired', 'duration']
    
    def get_certificate_file_url(self, obj):
        if obj.certificate_file:
            return obj.certificate_file.url
        return None
    
    def validate_issue_date(self, value):
        """Validate issue date is not in the future"""
        if value > timezone.now().date():
            raise serializers.ValidationError("Issue date cannot be in the future")
        return value
    
    def validate_expiry_date(self, value):
        """Validate expiry date is after issue date"""
        issue_date = self.initial_data.get('issue_date')
        if issue_date and value:
            if value < issue_date:
                raise serializers.ValidationError("Expiry date must be after issue date")
        return value
    
    def validate(self, data):
        """Additional validation"""
        # Check if certification already exists for this user
        profile = self.context.get('profile')
        if profile and 'title' in data and 'issuer' in data:
            existing = Certification.objects.filter(
                profile=profile,
                title__iexact=data['title'],
                issuer__iexact=data['issuer']
            ).exists()
            if existing:
                raise serializers.ValidationError(
                    "You already have this certification"
                )
        return data
    
    def create(self, validated_data):
        profile = self.context.get('profile')
        if not profile:
            raise serializers.ValidationError("Profile is required")
        return Certification.objects.create(profile=profile, **validated_data)

class ProjectSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = Project
        fields = "__all__"


class GroupMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = GroupMember
        fields = ['id', 'user_id', 'username', 'email', 'role', 'joined_at']
        read_only_fields = ['joined_at']

class GroupSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    is_member = serializers.SerializerMethodField()
    my_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'category', 'activity_status',
            'created_by', 'created_by_username', 'created_by_email',
            'cover_image', 'is_private', 'created_at',
            'member_count', 'is_member', 'my_role'
        ]
        read_only_fields = ['created_by', 'created_at', 'member_count']
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(user=request.user).exists()
        return False
    
    def get_my_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            member = obj.members.filter(user=request.user).first()
            return member.role if member else None
        return None
    
    def validate_name(self, value):
        """Ensure group name is unique"""
        if Group.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A group with this name already exists.")
        return value

class GroupDiscussionSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    
    class Meta:
        model = GroupDiscussion
        fields = ['id', 'content', 'author', 'author_username', 'author_email', 'created_at']
        read_only_fields = ['author', 'created_at']
    
    def validate_content(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Content cannot be empty.")
        return value.strip()


class GroupEventSerializer(serializers.ModelSerializer):
    month = serializers.CharField(read_only=True)
    day = serializers.IntegerField(read_only=True)
    formatted_date = serializers.CharField(read_only=True)
    
    class Meta:
        model = GroupEvent
        fields = [
            'id', 'title', 'description', 'date', 'location',
            'month', 'day', 'formatted_date', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate_date(self, value):
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Event date cannot be in the past.")
        return value
class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = "__all__"

class GroupChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = GroupChatMessage
        fields = [
            'id', 'message', 'message_type', 'user', 'username', 'user_email',
            'created_at', 'is_read'
        ]
        read_only_fields = ['user', 'created_at', 'is_read']
        
class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification settings (PATCH /api/users/settings/notifications/)"""
    
    class Meta:
        model = UserSettings
        fields = [
            'email_notifications',
            'community_updates', 
            'job_alerts',
            'event_reminders'
        ]

class PrivacySettingsSerializer(serializers.ModelSerializer):
    """Serializer for privacy settings (PATCH /api/users/settings/privacy/)"""
    
    class Meta:
        model = UserSettings
        fields = [
            'profile_visibility',
            'show_activity_status'
        ]

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password (POST /api/users/settings/change-password/)"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        # Check new passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        
        # Validate new password strength
        validate_password(data['new_password'])
        
        return data
    
    def validate_old_password(self, value):
        # Check old password is correct
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields= "__all__"
        
class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = "__all__"  
        
class UserActivityStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model =UserActivityStats
        fields= "__all__"
        
class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = "__all__"
        
class JobListSerializer(serializers.ModelSerializer):
    salary = serializers.CharField(source='salary_display', read_only=True)
    posted_at_display = serializers.CharField(source='posted_time_ago', read_only=True)
    is_bookmarked = serializers.SerializerMethodField()
    company_logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'company_logo_url',
            'location', 'job_type', 'salary', 'posted_at_display',
            'tags', 'is_bookmarked', 'is_featured', 'is_remote'
        ]
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False
    
    def get_company_logo_url(self, obj):
        if obj.company_logo:
            return obj.company_logo.url
        return None

class CourseSerializer(serializers.ModelSerializer):
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'instructor', 'description', 'duration',
            'level', 'category', 'enrolled_count', 'is_enrolled'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(user=request.user).exists()
        return False


class EnrolledCourseSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_instructor = serializers.CharField(source='course.instructor.username', read_only=True)
    course_duration = serializers.IntegerField(source='course.duration', read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'course_id', 'course_title', 'course_instructor',
            'course_duration', 'progress', 'enrolled_at', 'completed_at'
        ]

class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_instructor = serializers.CharField(source='course.instructor.username', read_only=True)
    
    class Meta:
        model = Certificate
        fields = ['id', 'course_title', 'course_instructor', 'issued_at', 'certificate_url']

class StudyGroupSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyGroup
        fields = ['id', 'name', 'course_title', 'member_count', 'created_at']
    
    def get_member_count(self, obj):
        return obj.members.count()

class ChallengeSerializer(serializers.ModelSerializer):
    is_participating = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'prize', 'deadline',
            'participants_count', 'category', 'is_participating'
        ]
    
    def get_is_participating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(user=request.user).exists()
        return False

# class AchievementSerializer(serializers.ModelSerializer):
#     class Meta:
#         pass


class JobDetailSerializer(serializers.ModelSerializer):
    salary = serializers.CharField(source='salary_display', read_only=True)
    posted_at_display = serializers.CharField(source='posted_time_ago', read_only=True)
    is_bookmarked = serializers.SerializerMethodField()
    company_logo_url = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'company_logo_url',
            'location', 'is_remote', 'job_type', 'experience_level',
            'salary', 'salary_min', 'salary_max', 'salary_currency',
            'is_salary_negotiable', 'description', 'requirements',
            'benefits', 'tags', 'posted_at_display', 'deadline',
            'is_bookmarked', 'has_applied', 'is_featured',
            'apply_email', 'apply_url', 'posted_at'
        ]
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False
    
    def get_has_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.applications.filter(user=request.user).exists()
        return False
    
    def get_company_logo_url(self, obj):
        if obj.company_logo:
            return obj.company_logo.url
        return None

class JobApplicationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    resume_url = serializers.SerializerMethodField()
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'cover_letter', 'resume', 'resume_url',
            'additional_docs', 'status', 'applied_at',
            'user_name', 'user_email', 'job_title'
        ]
        read_only_fields = ['status', 'applied_at']
    
    def get_resume_url(self, obj):
        if obj.resume:
            return obj.resume.url
        return None
    
    def create(self, validated_data):
        job = self.context.get('job')
        user = self.context.get('user')
        
        if JobApplication.objects.filter(job=job, user=user).exists():
            raise serializers.ValidationError("You have already applied for this job")
        
        return JobApplication.objects.create(job=job, user=user, **validated_data)
    
    
    
    
