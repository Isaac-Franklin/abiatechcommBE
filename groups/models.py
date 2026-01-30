from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

class Group(models.Model):
    CATEGORY_CHOICES = [
        ('technology', 'Technology'),
        ('sports', 'Sports'),
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('business', 'Business'),
        ('health', 'Health & Fitness'),
        ('gaming', 'Gaming'),
        ('art', 'Art & Design'),
        ('music', 'Music'),
        ('other', 'Other'),
    ]
    ACTIVITY_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    activity_status = models.CharField(
        max_length=20, 
        choices=ACTIVITY_STATUS_CHOICES, 
        default='active'
    )
    created_by = models.ForeignKey(
        User, 
        related_name='created_groups', 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Add these useful fields
    cover_image = models.ImageField(upload_to='group_covers/', blank=True, null=True)
    is_private = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.members.count()  # Count related GroupMembers
class GroupMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]
    group = models.ForeignKey(Group, related_name='members', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='group_memberships', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('group', 'user')  # User can only join a group once
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name} ({self.role})"
class GroupDiscussion(models.Model):
    group = models.ForeignKey('Group', related_name='discussions', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='group_discussions', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Discussion by {self.author.username} in {self.group.name}"
class GroupChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('file', 'File'),
        ('image', 'Image'),
    ]
    group = models.ForeignKey(Group, related_name='chat_messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='group_messages', on_delete=models.CASCADE)
    message = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    file = models.FileField(upload_to='group_chat_files/', blank=True, null=True)
    image = models.ImageField(upload_to='group_chat_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    class Meta:
        ordering = ['created_at']
    def __str__(self):
        if self.message_type == 'text':
            return f"{self.user.username}: {self.message[:30]}"
        elif self.message_type == 'file':
            return f"{self.user.username} sent a file. [{self.file}]"
        elif self.message_type == 'image':
            return f"{self.user.username} sent an image. [{self.image}]"
        return f"{self.user.username}: {self.message[:30]}"
    @property
    def file_url(self):
        if self.file:
            return self.file.url
        return None
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None
    
class GroupEvent(models.Model):
    group = models.ForeignKey('Group', related_name='events', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def month(self):
        """Get abbreviated month name"""
        return self.date.strftime('%b').upper()
    
    @property
    def day(self):
        """Get day of month"""
        return self.date.day
    
    @property
    def formatted_date(self):
        """Get date in YYYY-MM-DD format"""
        return self.date.strftime('%Y-%m-%d')
    
    class Meta:
        ordering = ['date']  # Order by date by default

    