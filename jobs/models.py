# models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead'),
        ('executive', 'Executive'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Location
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    
    # Job Details
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)
    
    # Salary
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='₦')
    is_salary_negotiable = models.BooleanField(default=False)
    
    # Description
    description = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField(blank=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)  # Store as list of strings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Contact
    apply_email = models.EmailField(blank=True)
    apply_url = models.URLField(blank=True)
    
    # Relations
    posted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='posted_jobs'
    )
    
    # Timestamps
    posted_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['job_type']),
            models.Index(fields=['location']),
            models.Index(fields=['salary_min', 'salary_max']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    @property
    def salary_display(self):
        """Format salary for display"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency}{self.salary_min:,.0f} - {self.salary_currency}{self.salary_max:,.0f}"
        elif self.salary_min:
            return f"{self.salary_currency}{self.salary_min:,.0f}+"
        elif self.salary_max:
            return f"Up to {self.salary_currency}{self.salary_max:,.0f}"
        return "Negotiable"
    
    @property
    def posted_time_ago(self):
        """Get human-readable time since posted"""
        delta = timezone.now() - self.posted_at
        
        if delta.days > 30:
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
        return "Just now"
    
    @property
    def is_expired(self):
        """Check if job has passed deadline"""
        if self.deadline:
            return timezone.now().date() > self.deadline
        return False

class JobBookmark(models.Model):
    """User bookmarks for jobs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_bookmarks')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-created_at']

class JobApplication(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    
    # Application details
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    additional_docs = models.FileField(upload_to='application_docs/', blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    # Employer notes
    notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_applications'
    )
    
    class Meta:
        unique_together = ['job', 'user']  # User can apply once per job
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.user.username} applied for {self.job.title}"