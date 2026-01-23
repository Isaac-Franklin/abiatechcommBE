# startups/models.py
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Startup(models.Model):
    STAGE_CHOICES = [
        ("idea", "Idea"),
        ("mvp", "MVP"),
        ("seed", "Seed"),
        ("growth", "Growth"),
        ("scale", "Scale"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    team_size = models.PositiveIntegerField()
    funding = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="startup_logos/", blank=True, null=True)
    founded_date = models.DateField()
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class StartupContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name="contacts")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class StartupProfile(models.Model):
    """Profile for Startups/Founders"""
    INDUSTRY_CHOICES = [
        ('fintech', 'FinTech'),
        ('healthtech', 'HealthTech'),
        ('edtech', 'EdTech'),
        ('agritech', 'AgriTech'),
        ('ecommerce', 'E-commerce'),
        ('saas', 'SaaS'),
        ('other', 'Other'),
    ]
    
    STAGE_CHOICES = [
        ('idea', 'Idea Stage'),
        ('mvp', 'MVP/Prototype'),
        ('early', 'Early Stage'),
        ('growth', 'Growth Stage'),
        ('scale', 'Scaling'),
    ]
    
    TEAM_SIZE_CHOICES = [
        ('1-5', '1-5 members'),
        ('6-10', '6-10 members'),
        ('11-25', '11-25 members'),
        ('26-50', '26-50 members'),
        ('50+', '50+ members'),
    ]
    
    FUNDING_STAGE_CHOICES = [
        ('bootstrapped', 'Bootstrapped'),
        ('pre-seed', 'Pre-Seed'),
        ('seed', 'Seed'),
        ('series-a', 'Series A'),
        ('series-b+', 'Series B+'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='startup_profile')
    company_name = models.CharField(max_length=200)
    company_website = models.URLField(blank=True)
    founded_year = models.IntegerField()
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    team_size = models.CharField(max_length=20, choices=TEAM_SIZE_CHOICES)
    funding_stage = models.CharField(max_length=20, choices=FUNDING_STAGE_CHOICES)
    product_description = models.TextField()
    target_market = models.TextField()
    revenue_model = models.TextField()
    current_revenue = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Startup: {self.company_name}"
