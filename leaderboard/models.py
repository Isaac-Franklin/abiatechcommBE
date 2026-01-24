from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Achievement(models.Model):
    """Model for user achievements/badges"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='User'
    )
    
    title = models.CharField(
        max_length=100,
        verbose_name='Achievement Title'
    )
    
    description = models.TextField(
        verbose_name='Description',
        help_text='What the user did to earn this achievement'
    )
    
    # Achievement type/category
    ACHIEVEMENT_TYPE_CHOICES = [
        ('engagement', 'Engagement'),
        ('content', 'Content Creation'),
        ('social', 'Social Interaction'),
        ('milestone', 'Milestone'),
        ('expertise', 'Expertise'),
        ('streak', 'Streak'),
        ('special', 'Special'),
    ]
    
    achievement_type = models.CharField(
        max_length=50,
        choices=ACHIEVEMENT_TYPE_CHOICES,
        default='engagement',
        verbose_name='Type'
    )
    
    # Badge/Icon
    BADGE_LEVEL_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    ]
    
    badge_level = models.CharField(
        max_length=20,
        choices=BADGE_LEVEL_CHOICES,
        default='bronze',
        verbose_name='Badge Level'
    )
    
    badge_icon = models.ImageField(
        upload_to='badge_icons/',
        verbose_name='Badge Icon',
        help_text='Icon for the achievement badge',
        blank=True,
        null=True
    )
    
    # Points awarded for this achievement
    points_awarded = models.PositiveIntegerField(
        default=0,
        verbose_name='Points Awarded'
    )
    
    # Timestamps
    earned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Earned At'
    )
    
    class Meta:
        ordering = ['-earned_at']
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
        indexes = [
            models.Index(fields=['user', 'earned_at']),
            models.Index(fields=['achievement_type']),
            models.Index(fields=['badge_level']),
        ]
        unique_together = ['user', 'title']  # User can only earn same achievement once
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_badge_color(self):
        """Get CSS color for badge level"""
        colors = {
            'bronze': '#CD7F32',
            'silver': '#C0C0C0',
            'gold': '#FFD700',
            'platinum': '#E5E4E2',
            'diamond': '#B9F2FF',
        }
        return colors.get(self.badge_level, '#000000')
    
    def time_since_earned(self):
        """Get human-readable time since earned"""
        now = timezone.now()
        delta = now - self.earned_at
        
        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

class PointTransaction(models.Model):
    """Model for tracking user points transactions"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='point_transactions',
        verbose_name='User'
    )
    
    points = models.IntegerField(
        verbose_name='Points',
        help_text='Positive for earned, negative for spent'
    )
    
    # Action types
    ACTION_TYPE_CHOICES = [
        ('post_created', 'Post Created'),
        ('comment_added', 'Comment Added'),
        ('post_liked', 'Post Liked'),
        ('achievement_earned', 'Achievement Earned'),
        ('daily_login', 'Daily Login'),
        ('profile_completed', 'Profile Completed'),
        ('content_shared', 'Content Shared'),
        ('review_added', 'Review Added'),
        ('service_created', 'Service Created'),
        ('startup_created', 'Startup Created'),
        ('referral', 'Referral'),
        ('purchase', 'Purchase'),
        ('reward_redeemed', 'Reward Redeemed'),
        ('penalty', 'Penalty'),
        ('other', 'Other'),
    ]
    
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPE_CHOICES,
        verbose_name='Action Type'
    )
    
    # Reference to related object (optional)
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Related Content Type'
    )
    
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Related Object ID'
    )
    
    description = models.CharField(
        max_length=255,
        verbose_name='Description',
        help_text='Brief description of the transaction'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Transaction Date'
    )
    
    # Expiry (for time-limited points)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expires At',
        help_text='When these points expire (if applicable)'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        sign = '+' if self.points > 0 else ''
        return f"{sign}{self.points} points for {self.user.username} - {self.action_type}"
    
    def is_positive(self):
        """Check if transaction adds points"""
        return self.points > 0
    
    def is_expired(self):
        """Check if points have expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def time_until_expiry(self):
        """Get time until expiry (if applicable)"""
        if self.expires_at:
            now = timezone.now()
            if now > self.expires_at:
                return "Expired"
            
            delta = self.expires_at - now
            if delta.days > 0:
                return f"{delta.days} days"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours} hours"
            else:
                minutes = delta.seconds // 60
                return f"{minutes} minutes"
        return "No expiry"
    
# In leaderboard/models.py
class UserActivityStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='activity_stats')
    
    # Activity counts
    posts_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    helps_count = models.IntegerField(default=0)
    
    # Points tracking (ADD THESE)
    total_points = models.IntegerField(default=0)
    points_last_week = models.IntegerField(default=0)
    points_last_month = models.IntegerField(default=0)
    
    # Achievements
    achievements_count = models.IntegerField(default=0)
    
    # Timestamps
    last_activity_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Activity Stats"
        verbose_name_plural = "User Activity Stats"
    
    def __str__(self):
        return f"{self.user.email} - {self.total_points} points"
    
    def calculate_total_points(self):
        """Calculate total points based on activities"""
        # Basic point system
        points = (
            self.posts_count * 10 +      # 10 points per post
            self.comments_count * 5 +    # 5 points per comment
            self.helps_count * 15        # 15 points per help
        )
        self.total_points = points
        self.save()
        return points
    
    
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_settings')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    community_updates = models.BooleanField(default=True)
    job_alerts = models.BooleanField(default=True)
    event_reminders = models.BooleanField(default=True)
    
    # Privacy settings
    profile_visibility = models.BooleanField(default=True)
    show_activity_status = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)