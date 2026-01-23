from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


User= get_user_model()

    
class Post(models.Model):
    author = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)  # Make optional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"Post by {self.author.username}"
    
    @property
    def like_count(self):
        return self.userspost.count()  # Count related PostLikes
    
    @property
    def comment_count(self):
        return self.comments.count()  # Count related PostComments
    
    @property
    def share_count(self):
        return self.postshare.count()  # Count related PostShares

class PostLike(models.Model):#PostLike Model
    user = models.ForeignKey(User, related_name="likes", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="userspost", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # User can only like a post once
    
    def __str__(self):
        return f"{self.user.username} liked {self.post}"

class PostComment(models.Model):
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)  # ← MISSING!
    content = models.TextField()
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['post', 'tag']
    def __str__(self):
        return self.tag.name
    
class Project(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )

    profile = models.ForeignKey(
        "onboarding.UserProfile",
        on_delete=models.CASCADE,
        related_name="projects"
    )

    title = models.CharField(max_length=150)
    description = models.TextField()

    category = models.CharField(
        max_length=100,
        blank=True
    )

    technologies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of technologies used"
    )

    github_url = models.URLField(
        blank=True,
        null=True
    )

    live_url = models.URLField(
        blank=True,
        null=True
    )

    cover_image = models.ImageField(
        upload_to="projects/covers/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    is_featured = models.BooleanField(default=False)

    started_at = models.DateField(blank=True, null=True)
    completed_at = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title
    
    
class PostShare(models.Model):
    user = models.ForeignKey(User, related_name="shares", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="postshare", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # User can only share a post once
    
    def __str__(self):
        return f"{self.user.username} shared {self.post}"

class Activity(models.Model):
    ACTION_TYPES = [
        ('post_created', 'Created a post'),
        ('post_liked', 'Liked a post'),
        ('post_commented', 'Commented on a post'),
        ('post_shared', 'Shared a post'),  # ← Add this
        ('user_followed', 'Followed a user'),
        ('profile_updated', 'Updated profile'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    
    # Generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return f"{self.user.username} {self.get_action_type_display()}"