from rest_framework import serializers
from groups.models import GroupChatMessage,Group, GroupDiscussion
from leaderboard.models import PointTransaction
from startups.models import Startup, StartupProfile, StartupContact
from marketplace.models import Service, ServiceContact, ServiceReview   
from api.serializers import UserSerializer
from jobs.models import Job
from django.contrib.auth import get_user_model
from community.models import Post, PostComment, Project
from api.serializers import (
    PostSerializer,StartupSerializer,PostCommentSerializer,
    GroupSerializer,GroupDiscussionSerializer,ProjectSerializer,
    GroupEventSerializer
    )
User = get_user_model()

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","email","first_name","last_name","username","password"]
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            username=validated_data.get('username', ''),
            user_type=User.UserType.ADMIN
        )
        return user
class AdminOverviewSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_content = serializers.IntegerField()
    new_users_7_days = serializers.IntegerField()
    active_users_30_days = serializers.IntegerField()
class AdminUserAnalyticsSerializer(serializers.Serializer):
    period = serializers.CharField()
    new_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_users = serializers.IntegerField()
    
class ServiceContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceContact
        fields = "__all__"
class SuspendedUserSerializer(serializers.Serializer):
    reason = serializers.CharField()
    suspended_at = serializers.DateTimeField()
    
class StartupStatsSerializer(serializers.Serializer):
    total_startups = serializers.IntegerField()
    total_funding = serializers.CharField()
    active_investors = serializers.IntegerField()
    jobs_created= serializers.IntegerField()
    class MonthGrowthSerializer(serializers.Serializer):
        startups_growth = serializers.CharField()
        funding_growth = serializers.CharField()

class ServiceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceReview
        fields = "__all__"
class PointTransactionSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = PointTransaction
        fields = "__all__"

class StartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = "__all__"
        read_only_fields = ['id']

class StartupContactSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StartupContact
        fields = "__all__"
        read_only_fields = ['id', 'user', 'created_at']


class StartupProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StartupProfile
        fields = "__all__"
        read_only_fields = ['id', 'user']
class LeaderboardUserSerializer(serializers.Serializer):
    """User info for leaderboard"""
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    avatar = serializers.URLField(required=False, allow_null=True)
    user_type = serializers.CharField(required=False)

class LeaderboardEntrySerializer(serializers.Serializer):
    """Single leaderboard entry"""
    rank = serializers.IntegerField()
    user = LeaderboardUserSerializer(read_only=True)
    total_points = serializers.IntegerField()
    is_current_user = serializers.BooleanField(default=False)

class LeaderboardResponseSerializer(serializers.Serializer):
    """Complete leaderboard response"""
    results = LeaderboardEntrySerializer(many=True)
    current_user_rank = serializers.IntegerField(required=False, allow_null=True)
    total_users = serializers.IntegerField()
class GroupChatMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupChatMessage
        fields = "__all__"
    
    def get_file_url(self, obj):
        return obj.file_url
    
    def get_image_url(self, obj):
        return obj.image_url
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
class AdminGetContentAnalytics(serializers.Serializer):
    posts = PostSerializer(read_only=True, many=True)
    posts_comments = PostCommentSerializer(read_only=True,many=True)
    jobs = JobSerializer(many=True,read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    groups_discussions = GroupDiscussionSerializer(read_only=True, many=True)
    groups_events = GroupEventSerializer(read_only=True,many=True)
    projects =ProjectSerializer(many=True, read_only=True)
    startup = StartupSerializer(many=True, read_only=True)
    
    
    