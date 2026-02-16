from django.shortcuts import render, redirect  # ← Added redirect
from django.contrib.auth import login, logout, authenticate  # ← Added authenticate
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from .authentication_serializers import UserRegistrationSerializer, StudentProfileSerializer  # Removed UserLoginSerializer

# Create your views here.
# Add these imports at the very top (after existing imports)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import json

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404

from .models import Student, College, Ranking
from .serializers import StudentSerializer, CollegeSerializer, RankingSerializer
from .recommendation_engine import RecommendationEngine
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')


def register_page(request):
    """Render the register page"""
    return render(request, 'recommendations/register.html')

@login_required
def profile_page(request):
    """Render the profile page with user data"""
    try:
        student_profile = Student.objects.get(user=request.user)
        context = {
            'student_profile': student_profile,
            'courses_list': student_profile.preferred_courses
        }
    except Student.DoesNotExist:
        # If no profile exists, create one with defaults
        student_profile = Student.objects.create(
            user=request.user,
            name=f"{request.user.first_name} {request.user.last_name}",
            email=request.user.email,
            marks=0.0,
            category='General',
            budget=0.0
        )
        context = {
            'student_profile': student_profile,
            'courses_list': []
        }
    
    return render(request,'recommendations/profile.html',context)

def home(request):
    return render(request,'recommendations/home.html')


def student_dashboard(request):
    return render(request,'recommendations/student_dashboard.html')


def college_list(request):
    return render(request,'recommendations/college_list.html')


def generate_recommendations_page(request):
    return render(request,'recommendations/generate_recommendations.html')


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class CollegeViewSet(ModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer


class GenerateRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Get logged-in user's student profile
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response(
                {'error':'Please complete your profile first'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if student profile is complete
        if not student.marks or not student.category:
            return Response(
                {'error': 'Please update your marks and category in profile'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use existing recommendation logic with this student
        colleges = College.objects.all()
        results = []
        
        for college in colleges:
            scores = RecommendationEngine.calculate_scores(student, college)
            total_score = RecommendationEngine.calculate_total_score(scores)
            star_rating = RecommendationEngine.calculate_star_rating(total_score)
            
            # Save ranking
            ranking, created = Ranking.objects.update_or_create(
                student=student,
                college=college,
                defaults={
                    'cutoff_score': scores.get('cutoff', 0),
                    'course_score': scores.get('course', 0),
                    'location_score': scores.get('location', 0),
                    'budget_score': scores.get('budget', 0),
                    'placement_score': scores.get('placement', 0),
                    'facility_score': scores.get('facility', 0),
                    'review_score': scores.get('review', 0),
                    'total_score': total_score,
                    'star_rating': star_rating,
                }
            )
            
            results.append({
                'college_id': college.id,
                'college_name': college.name,
                'location': college.location,
                'total_score': total_score,
                'star_rating': star_rating,
                'annual_fees': college.annual_fees,
                'placement_rate': college.placement_rate
            })
        
        # Sort by score
        results = sorted(results,key=lambda x: x['total_score'], reverse=True)
        
        return Response({
            'student': student.user.username,
            'recommendations': results
        })


class FilterRecommendationsView(APIView):
    def get(self, request):
        student_id = request.query_params.get('student_id')
        min_stars = request.query_params.get('min_stars', 0)
        location = request.query_params.get('location')
        max_fees = request.query_params.get('max_fees')
        
        student = get_object_or_404(Student, id=student_id)
        
        # Base queryset
        rankings = Ranking.objects.filter(student=student)
        
        # Apply filters
        if min_stars:
            rankings = rankings.filter(star_rating__gte=float(min_stars))
        
        if location:
            rankings = rankings.filter(college__location__icontains=location)
        
        if max_fees:
            rankings = rankings.filter(college__annual_fees__lte=float(max_fees))
        
        # Sort by score
        rankings = rankings.order_by('-total_score')
        serializer = RankingSerializer(rankings, many=True)
        
        return Response(serializer.data)


#--------------------------------------------------------------
def login_page(request):
    """Render the login page"""
    return render(request,'recommendations/login.html')


def login_user(request):
    """Handle HTML form login (for the web interface)"""
    if request.method == 'POST':
        username_or_email = request.POST.get('username') or request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request,'recommendations/login.html', {
                'error': 'Invalid email/username or password'
            })
    
    return render(request, 'recommendations/login.html')


# views.py - Update UserRegistrationView
class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # FIXED: Add all required fields when creating student profile
                student = Student.objects.create(
                    user=user,
                    name=f"{user.first_name} {user.last_name}",
                    email=user.email,
                    marks=0.0,          # ← ADD THIS (required field)
                    category='General',  # ← ADD THIS (required field)
                    budget=0.0          # ← ADD THIS (default value)
                )
                
                # Create token for authentication
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'message': 'Registration successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    },
                    'token': token.key
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Catch any unexpected errors
            return Response({
                'error': str(e),
                'detail': 'An unexpected error occurred during registration'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# SINGLE UserLoginView class (remove duplicates)
class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            username_or_email = request.data.get('username') or request.data.get('email')
            password = request.data.get('password')
            
            if not username_or_email or not password:
                return Response(
                    {'error': 'Please provide username/email and password'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = authenticate(request, username=username_or_email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Get or create token
                token, created = Token.objects.get_or_create(user=user)
                
                # Get student profile if exists
                try:
                    student = Student.objects.get(user=user)
                    profile_data = StudentProfileSerializer(student).data
                except Student.DoesNotExist:
                    profile_data = None
                
                return Response({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    },
                    'profile': profile_data,
                    'token': token.key
                })
            
            return Response(
                {'error': 'Invalid username/email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        except Exception as e:
            return Response({
                'error': str(e),
                'detail': 'An unexpected error occurred during login'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLogoutView(APIView):  # ← ADD THIS MISSING CLASS
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Delete token
        try:
            Token.objects.filter(user=request.user).delete()
        except:
            pass
        
        logout(request)
        return Response({'message': 'Logout successful'})


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        try:
            student = Student.objects.get(user=user)
            serializer = StudentProfileSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'message': 'Student profile not set up yet'
            })


class UpdateStudentProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # Update student profile
        student.marks = request.data.get('marks', student.marks)
        student.category = request.data.get('category', student.category)
        student.preferred_courses = request.data.get('preferred_courses', student.preferred_courses)
        student.preferred_location = request.data.get('preferred_location', student.preferred_location)
        student.budget = request.data.get('budget', student.budget)
        student.save()
        
        # Update user info if provided
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        
        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)
    # Add this function to handle web form registration
def register_user(request):
    """Handle HTML form registration (for the web interface)"""
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Basic validation
        if password != confirm_password:
            return render(request, 'recommendations/register.html', {
                'error': 'Passwords do not match'
            })
        
        if User.objects.filter(username=username).exists():
            return render(request, 'recommendations/register.html', {
                'error': 'Username already exists'
            })
        
        if User.objects.filter(email=email).exists():
            return render(request, 'recommendations/register.html', {
                'error': 'Email already registered'
            })
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create student profile
            student = Student.objects.create(
                user=user,
                name=f"{first_name} {last_name}",
                email=email,
                marks=0.0,
                category='General',
                budget=0.0
            )
            
            # Auto-login after registration
            login(request, user)
            return redirect('dashboard')
            
        except Exception as e:
            return render(request, 'recommendations/register.html', {
                'error': f'Registration failed: {str(e)}'
            })
    
    # GET request - show form
    return render(request, 'recommendations/register.html')

@login_required
def edit_profile(request):
    """Handle profile editing"""
    try:
        student_profile = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        # Create a profile if it doesn't exist
        student_profile = Student.objects.create(
            user=request.user,
            name=f"{request.user.first_name} {request.user.last_name}",
            email=request.user.email,
            marks=0.0,
            category='General',
            budget=0.0
        )
    
    if request.method == 'POST':
        try:
            # Update user information
            user = request.user
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            # Update student profile
            student_profile.name = f"{user.first_name} {user.last_name}"
            student_profile.email = user.email
            student_profile.marks = float(request.POST.get('marks', student_profile.marks))
            student_profile.category = request.POST.get('category', student_profile.category)
            student_profile.budget = float(request.POST.get('budget', student_profile.budget))
            
            # Handle preferred courses (convert comma-separated to list)
            courses_input = request.POST.get('preferred_courses', '')
            if courses_input:
                courses_list = [course.strip() for course in courses_input.split(',') if course.strip()]
                student_profile.preferred_courses = courses_list
            
            # Handle preferred location
            student_profile.preferred_location = request.POST.get('preferred_location', student_profile.preferred_location)
            
            student_profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_page')  # Redirect to profile page
            
        except Exception as e:
            return render(request, 'recommendations/edit_profile.html', {
                'error': f'Error updating profile: {str(e)}',
                'student_profile': student_profile
            })
    
    # GET request - show form with current data
    return render(request, 'recommendations/edit_profile.html', {
        'student_profile': student_profile
    })