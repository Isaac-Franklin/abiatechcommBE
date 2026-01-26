from rest_framework import serializers
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


class ServiceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceReview
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