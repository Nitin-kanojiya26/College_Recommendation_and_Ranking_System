from django.contrib import admin
from django import forms
from .models import Student, College, Ranking


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'marks', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'email']


class CollegeAdminForm(forms.ModelForm):
    """Admin form that lets you edit courses and facilities as simple comma lists."""

    courses_offered = forms.CharField(
        required=False,
        help_text="Comma-separated list, e.g. BTech, BSc, MBA",
        widget=forms.TextInput,
        label="Courses offered",
    )
    facilities = forms.CharField(
        required=False,
        help_text="Comma-separated list, e.g. Hostel, Library, Sports",
        widget=forms.TextInput,
        label="Facilities",
    )

    class Meta:
        model = College
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert list from DB into comma string for display
        if self.instance and self.instance.pk:
            if isinstance(self.instance.courses_offered, list):
                self.fields['courses_offered'].initial = ", ".join(self.instance.courses_offered)
            if isinstance(self.instance.facilities, list):
                self.fields['facilities'].initial = ", ".join(self.instance.facilities)

    def clean_courses_offered(self):
        value = self.cleaned_data.get('courses_offered', '')
        if not value:
            return []
        return [c.strip() for c in value.split(',') if c.strip()]

    def clean_facilities(self):
        value = self.cleaned_data.get('facilities', '')
        if not value:
            return []
        return [f.strip() for f in value.split(',') if f.strip()]


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    form = CollegeAdminForm
    list_display = ['name', 'location', 'annual_fees', 'placement_rate', 'review_score']
    list_filter = ['location']
    search_fields = ['name', 'location']


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ['student', 'college', 'total_score', 'star_rating', 'created_at']
    list_filter = ['created_at', 'star_rating']
    search_fields = ['student__name', 'college__name']