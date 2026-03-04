from django.contrib import admin
from django import forms
from .models import Student, College, Ranking

class CollegeAdminForm(forms.ModelForm):
    class Meta:
        model = College
        fields = '__all__'
        widgets = {
            'courses_offered': forms.Textarea(attrs={'rows': 3, 'cols': 50, 'placeholder': 'BTech, BSc, MBA'}),
            'facilities': forms.Textarea(attrs={'rows': 3, 'cols': 50, 'placeholder': 'Hostel, Library, Sports, Lab'}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    form = CollegeAdminForm
    list_display = ['name', 'location', 'display_courses', 'annual_fees', 'placement_rate', 'review_score']
    list_filter = ['location']
    search_fields = ['name', 'location']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'description', 'annual_fees')
        }),
        ('Courses Offered', {
            'fields': ('courses_offered',),
            'description': 'Enter courses separated by commas (e.g., BTech, BSc, MBA)'
        }),
        ('Facilities', {
            'fields': ('facilities',),
            'description': 'Enter facilities separated by commas (e.g., Hostel, Library, Sports, Lab)'
        }),
        ('Cut-off Marks', {
            'fields': ('cutoff_general', 'cutoff_obc', 'cutoff_sc', 'cutoff_st'),
        }),
        ('Placement & Reviews', {
            'fields': ('placement_rate', 'avg_package', 'review_score'),
        }),
    )

    def display_courses(self, obj):
        courses = obj.get_courses_list()
        if courses:
            return ', '.join(courses[:3]) + ('...' if len(courses) > 3 else '')
        return '-'
    display_courses.short_description = 'Courses'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'marks', 'category', 'display_preferred_courses', 'preferred_location', 'budget']
    list_filter = ['category', 'preferred_location']
    search_fields = ['name', 'email', 'user__username']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'email')
        }),
        ('Academic Information', {
            'fields': ('marks', 'category')
        }),
        ('Preferences', {
            'fields': ('preferred_courses', 'preferred_location', 'budget', 'min_rating'),
        }),
    )

    def display_preferred_courses(self, obj):
        courses = obj.get_preferred_courses_list()
        if courses:
            return ', '.join(courses[:3]) + ('...' if len(courses) > 3 else '')
        return '-'
    display_preferred_courses.short_description = 'Preferred Courses'

@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ['student', 'college', 'total_score', 'star_rating', 'created_at']
    list_filter = ['created_at', 'star_rating']
    search_fields = ['student__name', 'college__name']