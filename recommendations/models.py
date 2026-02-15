from django.db import models
from django.contrib.auth.models import User
class College(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ]

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Courses offered (store as JSON or separate model)
    courses_offered = models.JSONField(default=list)
    
    # Fees
    annual_fees = models.FloatField(default=0)
    
    # Facilities
    facilities = models.JSONField(default=list)  # ['Hostel', 'Library', 'Sports', 'Lab']
    
    # Category-wise cutoffs
    cutoff_general = models.FloatField(default=0)
    cutoff_obc = models.FloatField(default=0)
    cutoff_sc = models.FloatField(default=0)
    cutoff_st = models.FloatField(default=0)
    
    # Placement data
    placement_rate = models.FloatField(default=0)  # Percentage
    avg_package = models.FloatField(default=0)     # In LPA
    
    # Reviews
    review_score = models.FloatField(default=0)    # 0-5
    
    def __str__(self):
        return self.name
    
    def get_cutoff(self, category):
        """Get cutoff for specific category"""
        cutoffs = {
            'General': self.cutoff_general,
            'OBC': self.cutoff_obc,
            'SC': self.cutoff_sc,
            'ST': self.cutoff_st,
        }
        return cutoffs.get(category, 0)

class Student(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    marks = models.FloatField(default=0.0)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='General')   
    # Preferences
    preferred_courses = models.JSONField(default=list)
    preferred_location = models.CharField(max_length=100, blank=True)
    budget = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Ranking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='rankings')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='rankings')
    
    # Score components
    cutoff_score = models.FloatField(default=0)
    course_score = models.FloatField(default=0)
    location_score = models.FloatField(default=0)
    budget_score = models.FloatField(default=0)
    placement_score = models.FloatField(default=0)
    facility_score = models.FloatField(default=0)
    review_score = models.FloatField(default=0)
    
    # Overall scores
    total_score = models.FloatField(default=0)  # 0-10
    star_rating = models.FloatField(default=0)  # 0-5
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'college']
        ordering = ['-total_score']
    
    def __str__(self):
        return f"{self.student.name} - {self.college.name}: {self.star_rating}★"