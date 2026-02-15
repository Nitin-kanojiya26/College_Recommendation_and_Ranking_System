from django.contrib import admin
from .models import Student, College, Ranking

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'marks', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'email']

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'annual_fees', 'placement_rate', 'review_score']
    list_filter = ['location']
    search_fields = ['name', 'location']
    filter_horizontal = []

@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ['student', 'college', 'total_score', 'star_rating', 'created_at']
    list_filter = ['created_at', 'star_rating']
    search_fields = ['student__name', 'college__name']