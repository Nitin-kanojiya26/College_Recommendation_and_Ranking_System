from rest_framework import serializers
from .models import Student, College, Ranking

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert JSON fields to proper format
        if isinstance(data.get('courses_offered'), str):
            data['courses_offered'] = eval(data['courses_offered'])
        if isinstance(data.get('facilities'), str):
            data['facilities'] = eval(data['facilities'])
        return data

class RankingSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    college_location = serializers.CharField(source='college.location', read_only=True)
    
    class Meta:
        model = Ranking
        fields = ['id', 'college_name', 'college_location', 'total_score', 
                  'star_rating', 'created_at']