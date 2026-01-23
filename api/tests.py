# api/tests.py - Complete fixed version
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from community.models import Post, PostComment, PostLike
from onboarding.models import MemberProfile
from startups.models import Startup
import json

User = get_user_model()


class AuthenticationTests(TestCase):
    """Tests for authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.login_url = '/api/v1/auth/login/'
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'userType': 'member',
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'password': 'SecurePass123!',
            'confirmPassword': 'SecurePass123!',
            'agreeToTerms': True,
            'profession': 'Software Developer',
            'skills': 'Python, Django',
            'interests': 'AI, Web Development'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        print(f"Registration response: {response.status_code}")
        # FIX: Use response.json() instead of response.data for JsonResponse
        print(f"Registration data: {response.json()}")
        
        self.assertEqual(response.status_code, 201)  # JsonResponse uses 201, not status.HTTP_201_CREATED
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
        
        # Verify profile was created
        user = User.objects.get(email='john@example.com')
        self.assertTrue(MemberProfile.objects.filter(user=user).exists())
    
    def test_user_registration_invalid_data(self):
        """Test registration with invalid data"""
        data = {
            'userType': 'member',
            'name': 'John Doe',
            'email': 'invalid-email',  # Invalid email
            'phone': '1234567890',
            'password': 'SecurePass123!',
            'confirmPassword': 'DifferentPass123!',  # Passwords don't match
            'agreeToTerms': True
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)  # JsonResponse uses 400
    
    def test_user_login_success(self):
        """Test successful user login"""
        # Create user first
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Create MemberProfile
        MemberProfile.objects.create(
            user=user,
            profession='Software Developer',
            phone='1234567890'
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        print(f"Login response: {response.status_code}")
        print(f"Login data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('access', response.data['token'])


class UserProfileTests(TestCase):
    """Tests for user profile endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        # Create MemberProfile
        self.profile = MemberProfile.objects.create(
            user=self.user,
            profession='Software Developer',
            phone='1234567890',
            skills='Python, Django',
            interests='AI, ML'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        self.profile_url = '/api/v1/auth/users/profile/'
    
    def test_get_user_profile(self):
        """Test getting user profile"""
        response = self.client.get(self.profile_url)
        
        print(f"Profile response: {response.status_code}")
        if response.status_code != 200:
            print(f"Profile error: {response.data}")
        else:
            print(f"Profile data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('email'), 'test@example.com')
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'profession': 'Senior Developer',
            'skills': 'Python, Django, React'
        }
        
        # Use multipart format since view has @parser_classes([MultiPartParser, FormParser])
        response = self.client.patch(self.profile_url, data, format='multipart')
        
        print(f"Update profile response: {response.status_code}")
        if response.status_code != 200:
            print(f"Update error: {response.data}")
        else:
            print(f"Update data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify updates
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')


class PasswordChangeTests(TestCase):
    """Tests for password change"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='OldPass123!'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        self.password_change_url = '/api/v1/auth/users/settings/change-password/'
    
    def test_change_password_success(self):
        """Test successful password change"""
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }
        
        response = self.client.post(self.password_change_url, data, format='json')
        
        print(f"Password change response: {response.status_code}")
        print(f"Password change data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StartupTests(TestCase):
    """Tests for startup endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        self.startup_url = '/api/v1/auth/startups/'
        
        # Create test startups
        Startup.objects.create(
            name='Startup 1',
            description='Description 1',
            category='Tech',
            stage='idea',
            team_size=3,
            founded_date='2023-01-01',
            location='Location 1'
        )
        Startup.objects.create(
            name='Startup 2',
            description='Description 2',
            category='Finance',
            stage='growth',
            team_size=10,
            founded_date='2022-01-01',
            location='Location 2'
        )
    
    def test_create_startup(self):
        """Test creating a startup"""
        data = {
            'name': 'New Startup',
            'description': 'A new innovative startup',
            'category': 'Technology',
            'stage': 'idea',
            'team_size': 5,
            'founded_date': '2024-01-01',
            'location': 'Silicon Valley'
        }
        
        print(f"Testing startup creation at: {self.startup_url}")
        
        # Try multipart first (because of @parser_classes)
        response = self.client.post(self.startup_url, data, format='multipart')
        
        print(f"Startup response: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Startup data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_startups(self):
        """Test listing startups"""
        response = self.client.get(self.startup_url)
        
        print(f"List startups response: {response.status_code}")
        print(f"List startups data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class PostTests(TestCase):
    """Tests for post endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Create post - using community.models.Post
        self.post = Post.objects.create(
            author=self.user,
            content='Test post content'
        )
        
        self.post_url = '/api/v1/posts/'
    
    def test_like_post(self):
        """Test liking a post"""
        url = f'{self.post_url}{self.post.id}/like/'
        response = self.client.post(url, format='json')
        
        print(f"Like post response: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Like post data: {response.data}")
        
        # Accept both 200 and 201
        self.assertIn(response.status_code, [200, 201])
        
        # Verify like was created
        self.assertTrue(PostLike.objects.filter(user=self.user, post=self.post).exists())
    
    def test_create_comment(self):
        """Test creating a comment"""
        url = f'{self.post_url}{self.post.id}/comments/'
        data = {
            'content': 'This is a test comment'
        }
        
        response = self.client.post(url, data, format='json')
        
        print(f"Create comment response: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Create comment data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify comment was created
        self.assertTrue(PostComment.objects.filter(author=self.user, post=self.post).exists())


# To run specific tests:
# python manage.py test api.tests.AuthenticationTests
# python manage.py test api.tests.AuthenticationTests.test_user_login_success
# python manage.py test api.tests.UserProfileTests
# python manage.py test api.tests.PostTests