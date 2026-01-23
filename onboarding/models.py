from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserProfile(models.Model):
    """Extended User profile with common fields"""
    USER_TYPE_CHOICES = [
        ('member', 'Community Member'),
        ('investor', 'Investor'),
        ('startup', 'Startup/Founder'),
        ('cofounder', 'Co-Founder'),
        ('incubator', 'Startup Incubator'),
        ('revops', 'Revenue Operations'),
        ('cto', 'CTO/Technical Lead'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bio = models.CharField(null=True,blank=True)
    location = models.CharField(null=True,blank=True)
    skill = models.CharField(max_length=20, null=True,  blank=True)
    
    def __str__(self):
        return f"{self.user.email} ({self.get_user_type_display()})"
    
class Certification(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='certifications')
    
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(max_length=500, blank=True)
    
    description = models.TextField(blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Files
    certificate_file = models.FileField(upload_to='certifications/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'
    
    def __str__(self):
        return f"{self.title} - {self.issuer}"
    
    def is_expired(self):
        """Check if certification is expired"""
        if self.expiry_date:
            from django.utils import timezone
            return timezone.now().date() > self.expiry_date
        return False
    
    def get_duration(self):
        """Get certification duration in years/months"""
        if self.expiry_date:
            months = (self.expiry_date.year - self.issue_date.year) * 12 + (self.expiry_date.month - self.issue_date.month)
            years = months // 12
            remaining_months = months % 12
            
            if years > 0:
                return f"{years} year{'s' if years > 1 else ''}"
            return f"{remaining_months} month{'s' if remaining_months > 1 else ''}"
        return "No expiry"
class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['profile', 'name']  # Prevent duplicate skills per user
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_proficiency_level_display()})"

class MemberProfile(models.Model):
    """Profile for Community Members"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    phone = models.CharField(max_length=200, blank=True, null=True)
    profession = models.CharField(max_length=200)
    skills = models.TextField()
    interests = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    def __str__(self):
        return f"Member: {self.user.email}"


class InvestorProfile(models.Model):
    """Profile for Investors"""
    INVESTOR_TYPE_CHOICES = [
        ('angel', 'Angel Investor'),
        ('vc', 'Venture Capital'),
        ('corporate', 'Corporate Investor'),
        ('family-office', 'Family Office'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investor_profile')
    investor_type = models.CharField(max_length=20, choices=INVESTOR_TYPE_CHOICES)
    investment_range = models.CharField(max_length=50)
    focus_sectors = models.TextField()
    previous_investments = models.TextField(blank=True)
    portfolio_size = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Investor: {self.user.email}"




class CofounderProfile(models.Model):
    """Profile for Co-Founders"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cofounder_profile')
    startup_name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    years_with_startup = models.IntegerField()
    expertise = models.TextField()
    product_description = models.TextField()
    
    def __str__(self):
        return f"Co-Founder: {self.user.email} at {self.startup_name}"


class IncubatorProfile(models.Model):
    """Profile for Startup Incubators"""
    PROGRAM_TYPE_CHOICES = [
        ('incubator', 'Incubator'),
        ('accelerator', 'Accelerator'),
        ('both', 'Both'),
        ('innovation-hub', 'Innovation Hub'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='incubator_profile')
    organization_name = models.CharField(max_length=200)
    organization_website = models.URLField()
    year_established = models.IntegerField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    startups_supported = models.IntegerField()
    support_services = models.TextField()
    success_stories = models.TextField(blank=True)
    application_process = models.TextField()
    
    def __str__(self):
        return f"Incubator: {self.organization_name}"


class RevOpsProfile(models.Model):
    """Profile for Revenue Operations"""
    EXPERIENCE_CHOICES = [
        ('0-2', '0-2 years'),
        ('3-5', '3-5 years'),
        ('6-10', '6-10 years'),
        ('10+', '10+ years'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='revops_profile')
    current_company = models.CharField(max_length=200)
    current_role = models.CharField(max_length=100)
    years_experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES)
    tools_expertise = models.TextField()
    specializations = models.TextField()
    achievements = models.TextField(blank=True)
    
    def __str__(self):
        return f"RevOps: {self.user.email}"


class CTOProfile(models.Model):
    """Profile for CTOs/Technical Leads"""
    TEAM_LEAD_CHOICES = [
        ('1-5', '1-5 developers'),
        ('6-15', '6-15 developers'),
        ('16-30', '16-30 developers'),
        ('30+', '30+ developers'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cto_profile')
    current_company = models.CharField(max_length=200)
    current_role = models.CharField(max_length=100)
    tech_stack = models.TextField()
    team_lead_experience = models.CharField(max_length=10, choices=TEAM_LEAD_CHOICES)
    projects_led = models.TextField()
    technical_expertise = models.TextField()
    
    def __str__(self):
        return f"CTO: {self.user.email}"