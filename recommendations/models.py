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
    description = models.TextField(blank=True, default='')
    
    # Courses offered (store as comma-separated string)
    courses_offered = models.TextField(
        help_text="Enter courses separated by commas (e.g., BTech, BSc, MBA)",
        blank=True,
        default=''
    )
    
    # Fees
    annual_fees = models.FloatField(default=0)
    
    # Facilities (store as comma-separated string)
    facilities = models.TextField(
        help_text="Enter facilities separated by commas (e.g., Hostel, Library, Sports, Lab)",
        blank=True,
        default=''
    )
    
    # Category-wise cutoffs
    cutoff_general = models.FloatField(default=0)
    cutoff_obc = models.FloatField(default=0)
    cutoff_sc = models.FloatField(default=0)
    cutoff_st = models.FloatField(default=0)
    
    # Placement data
    placement_rate = models.FloatField(default=0)
    avg_package = models.FloatField(default=0)
    
    # Reviews
    review_score = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_courses_list(self):
        """Return courses as list"""
        if self.courses_offered:
            return [c.strip() for c in self.courses_offered.split(',') if c.strip()]
        return []
    
    def get_facilities_list(self):
        """Return facilities as list"""
        if self.facilities:
            return [f.strip() for f in self.facilities.split(',') if f.strip()]
        return []
    
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
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    name = models.CharField(max_length=100, default='')
    email = models.EmailField(default='')
    marks = models.FloatField(default=0.0)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='General')
    
    # Preferences (store as comma-separated strings)
    preferred_courses = models.TextField(
        help_text="Enter preferred courses separated by commas",
        blank=True,
        default=''
    )
    preferred_location = models.CharField(max_length=100, blank=True, default='')
    budget = models.FloatField(default=0)
    min_rating = models.FloatField(default=3.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name or self.user.username
    
    def get_preferred_courses_list(self):
        """Return preferred courses as list"""
        if self.preferred_courses:
            return [c.strip() for c in self.preferred_courses.split(',') if c.strip()]
        return []
    
    def save(self, *args, **kwargs):
        if not self.name and self.user:
            self.name = f"{self.user.first_name} {self.user.last_name}".strip()
        if not self.email and self.user:
            self.email = self.user.email
        super().save(*args, **kwargs)

class Ranking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='rankings')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='rankings')
    
    total_score = models.FloatField(default=0)
    star_rating = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'college']
        ordering = ['-total_score']
    
    def __str__(self):
        return f"{self.student.name} - {self.college.name}"