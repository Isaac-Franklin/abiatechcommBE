from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User=get_user_model()

class Service(models.Model):
    """Main Service model (from previous implementation)"""
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    # Helper methods
    def average_rating(self):
        """Calculate average rating for this service"""
        reviews = self.reviews.all()
        if reviews.exists():
            return sum([review.rating for review in reviews]) / reviews.count()
        return 0
    
    def review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()

class ServiceReview(models.Model):
    """Model for user reviews/ratings of services"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_reviews'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only review a service once
        unique_together = ['user', 'service']
        ordering = ['-created_at']
        verbose_name = 'Service Review'
        verbose_name_plural = 'Service Reviews'
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.service.title}"
    
    def get_rating_display(self):
        """Get star representation of rating"""
        return '★' * self.rating + '☆' * (5 - self.rating)

class ServiceContact(models.Model):
    """Model for contacting service providers"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_contacts'
    )
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='contact_messages'
    )
    
    message = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Add status field for message tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Optional: For replies
    reply = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Contact'
        verbose_name_plural = 'Service Contacts'
    
    def __str__(self):
        return f"Contact from {self.user.username} about {self.service.title}"