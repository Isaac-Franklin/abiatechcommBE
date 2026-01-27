from rest_framework import serializers
from leaderboard.models import PointTransaction
from startups.models import Startup, StartupProfile, StartupContact
from marketplace.models import Service, ServiceContact, ServiceReview   
from api.serializers import UserSerializer

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ServiceContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceContact
        fields = "__all__"

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
