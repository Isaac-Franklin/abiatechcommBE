from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    CATEGORY_CHOICES = [
        ('technology', 'Technology'),
        ('business', 'Business'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('data_science', 'Data Science'),
        ('programming', 'Programming'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    instructor = models.ForeignKey(User, related_name='courses_taught', on_delete=models.CASCADE)
    description = models.TextField()
    duration = models.PositiveIntegerField()  # in hours or minutes
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    enrolled_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title


class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, related_name='course_enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)  # percentage 0-100
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'course')
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class Certificate(models.Model):
    user = models.ForeignKey(User, related_name='certificates', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='certificates', on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_url = models.URLField()
    
    def __str__(self):
        return f"Certificate for {self.user.username} - {self.course.title}"


class StudyGroup(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, related_name='study_groups', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='study_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.course.title}"


class Challenge(models.Model):
    CATEGORY_CHOICES = [
        ('coding', 'Coding'),
        ('design', 'Design'),
        ('writing', 'Writing'),
        ('video', 'Video'),
        ('photography', 'Photography'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    prize = models.CharField(max_length=255)
    deadline = models.DateTimeField()
    participants_count = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    def __str__(self):
        return self.title


class ChallengeParticipant(models.Model):
    user = models.ForeignKey(User, related_name='challenge_participations', on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, related_name='participants', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    submission = models.TextField(blank=True)  # or FileField/URLField depending on submission type
    
    class Meta:
        unique_together = ('user', 'challenge')
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"
