from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Student, College, Ranking

def home(request):
    return render(request, 'recommendations/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'recommendations/login.html', {
                'error': 'Invalid username or password'
            })
    
    return render(request, 'recommendations/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if password != password2:
            return render(request, 'recommendations/register.html', {
                'error': 'Passwords do not match'
            })
        
        if User.objects.filter(username=username).exists():
            return render(request, 'recommendations/register.html', {
                'error': 'Username already exists'
            })
        
        if User.objects.filter(email=email).exists():
            return render(request, 'recommendations/register.html', {
                'error': 'Email already exists'
            })
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create student profile
        Student.objects.create(
            user=user,
            name=f"{first_name} {last_name}".strip(),
            email=email,
            marks=0,
            category='General',
            preferred_courses='',
            preferred_location='',
            budget=0,
            min_rating=3.0
        )
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'recommendations/register.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    # Get distinct locations for filter
    locations = College.objects.values_list('location', flat=True).distinct().order_by('location')
    locations = [loc for loc in locations if loc]
    
    # Get all courses from all colleges
    all_courses = set()
    for college in College.objects.all():
        courses = college.get_courses_list()
        all_courses.update(courses)
    all_courses = sorted(list(all_courses))
    
    context = {
        'student': student,
        'user': request.user,
        'locations': locations,
        'all_courses': all_courses
    }
    return render(request, 'recommendations/student_dashboard.html', context)

@login_required
def save_dashboard_preferences(request):
    if request.method == 'POST':
        try:
            student = Student.objects.get(user=request.user)
            
            # Get selected courses from checkboxes
            selected_courses = request.POST.getlist('courses')
            student.preferred_courses = ','.join(selected_courses)
            
            # Get location
            student.preferred_location = request.POST.get('location', '')
            
            # Get budget and min rating
            budget_val = request.POST.get('budget', '0')
            student.budget = float(budget_val) if budget_val else 0
            
            min_rating_val = request.POST.get('min_rating', '3')
            student.min_rating = float(min_rating_val) if min_rating_val else 3.0
            
            student.save()
            
            messages.success(request, 'Preferences saved successfully!')
        except Exception as e:
            messages.error(request, f'Error saving preferences: {str(e)}')
        
        return redirect('dashboard')
    
# @login_required
def college_list(request):
    colleges = College.objects.all()

    # Get distinct locations
    locations = College.objects.values_list('location', flat=True).distinct().order_by('location')
    locations = [loc for loc in locations if loc]

    # Get all unique courses
    all_courses = set()
    for college in colleges:
        courses = college.get_courses_list()
        all_courses.update(courses)
    all_courses = sorted(list(all_courses))

    # Get filters
    search = request.GET.get('search')
    location = request.GET.get('location')
    course = request.GET.get('course')
    fees = request.GET.get('fees')
    min_rating = request.GET.get('min_rating')

    filtered_colleges = []

    for college in colleges:
        include = True

        if search and search.lower() not in college.name.lower() and search.lower() not in college.location.lower():
            include = False

        if location and location != college.location:
            include = False

        if course:
            courses = college.get_courses_list()
            if course not in courses:
                include = False

        if fees:
            try:
                min_fees, max_fees = fees.split('-')
                if not (float(min_fees) <= college.annual_fees <= float(max_fees)):
                    include = False
            except:
                pass

        if min_rating:
            if college.review_score < float(min_rating):
                include = False

        if include:
            filtered_colleges.append(college)

    # ✅ SORT AFTER LOOP (inside function)
    filtered_colleges.sort(key=lambda x: x.review_score, reverse=True)

    context = {
        'colleges': filtered_colleges,
        'locations': locations,
        'all_courses': all_courses
    }

    return render(request, 'recommendations/college_list.html', context)
@login_required
def edit_profile(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = Student(user=request.user)
    
    if request.method == 'POST':
        # Update user information
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update or create student profile
        student.user = request.user
        student.name = f"{request.user.first_name} {request.user.last_name}".strip()
        student.email = request.user.email
        student.marks = float(request.POST.get('marks', 0))
        student.category = request.POST.get('category', 'General')
        
        # Handle preferred courses
        preferred_courses = request.POST.get('preferred_courses', '')
        if preferred_courses:
            courses = [c.strip() for c in preferred_courses.split(',') if c.strip()]
            student.preferred_courses = ','.join(courses)
        else:
            student.preferred_courses = ''
        
        student.preferred_location = request.POST.get('preferred_location', '')
        
        budget_val = request.POST.get('budget', '0')
        student.budget = float(budget_val) if budget_val else 0
        
        student.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'user': request.user,
        'student_profile': student
    }
    return render(request, 'recommendations/edit_profile.html', context)

@login_required
def profile_view(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    context = {
        'user': request.user,
        'student_profile': student
    }
    return render(request, 'recommendations/profile.html', context)

@login_required
def generate_recommendations(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('studentName')
        email = request.POST.get('studentEmail')
        marks = float(request.POST.get('marks', 0))
        category = request.POST.get('category', 'General')
        preferred_course = request.POST.get('preferred_course', '')
        preferred_location = request.POST.get('preferred_location', '')
        budget = float(request.POST.get('budget', 0)) if request.POST.get('budget') else 0
        min_rating = float(request.POST.get('min_rating', 0))
        
        # Create student data dict
        student_data = {
            'name': name,
            'email': email,
            'marks': marks,
            'category': category,
            'preferred_course': preferred_course,
            'preferred_location': preferred_location,
            'budget': budget,
            'min_rating': min_rating
        }
        request.session['student_data'] = student_data
        
        # Get all colleges
        all_colleges = College.objects.all()
        
        # Filter colleges
        filtered_colleges = []
        for college in all_colleges:
            include = True
            
            # Location filter
            if preferred_location and preferred_location.lower() not in college.location.lower():
                include = False
            
            # Course filter
            if preferred_course:
                courses = college.get_courses_list()
                if preferred_course not in courses:
                    include = False
            
            # Budget filter
            if budget > 0 and college.annual_fees > budget:
                include = False
            
            # Rating filter
            if min_rating > 0 and college.review_score < min_rating:
                include = False
            
            if include:
                filtered_colleges.append(college)
        
        # Calculate scores for each college
        recommendations = []
        for college in filtered_colleges:
            score = calculate_match_score(marks, category, preferred_course, preferred_location, budget, college)
            if score > 0:
                recommendations.append({
                    'college': college,
                    'score': round(score, 1),
                    'stars': round(score / 2, 1)
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        recommendations = recommendations[:10]
        
        context = {
            'student': student_data,
            'recommendations': recommendations
        }
        return render(request, 'recommendations/results.html', context)
    
    # GET request - show the form
    # Get all distinct courses and locations
     
    colleges = College.objects.all()
    all_courses = set()
    locations = set()
    
    for college in colleges:
        if college.location:
            locations.add(college.location)
        courses = college.get_courses_list()
        all_courses.update(courses)
    
    context = {
        'all_courses': sorted(list(all_courses)),
        'locations': sorted(list(locations))
    }
    return render(request, 'recommendations/generate_recommendations.html', context)

def calculate_match_score(marks, category, preferred_course, preferred_location, budget, college):
    """Calculate match score between student and college (0-10 scale)."""
    score = 0
    weights = {
        'cutoff': 0.30,
        'course': 0.20,
        'location': 0.15,
        'budget': 0.15,
        'placement': 0.10,
        'review': 0.10
    }
    
    # 1. Cutoff match (30%)
    cutoff = college.get_cutoff(category)
    if cutoff > 0:
        if marks >= cutoff:
            score += weights['cutoff'] * 10
        else:
            score += weights['cutoff'] * 10 * (marks / cutoff)
    
    # 2. Course match (20%)
    if preferred_course:
        courses = college.get_courses_list()
        if preferred_course in courses:
            score += weights['course'] * 10
    
    # 3. Location match (15%)
    if preferred_location and college.location:
        if preferred_location.lower() == college.location.lower():
            score += weights['location'] * 10
        elif preferred_location.lower() in college.location.lower() or college.location.lower() in preferred_location.lower():
            score += weights['location'] * 7
    
    # 4. Budget match (15%)
    if budget > 0 and college.annual_fees > 0:
        if college.annual_fees <= budget:
            score += weights['budget'] * 10
        else:
            ratio = budget / college.annual_fees
            score += weights['budget'] * 10 * min(ratio, 1)
    
    # 5. Placement rate (10%)
    if college.placement_rate > 0:
        score += weights['placement'] * 10 * (college.placement_rate / 100)
    
    # 6. Review score (10%)
    if college.review_score > 0:
        score += weights['review'] * 10 * (college.review_score / 5)
    
    return score

@login_required
def save_college(request):
    if request.method == 'POST':
        college_id = request.POST.get('college_id')
        messages.success(request, 'College saved successfully!')
        return redirect('college_list')
    return redirect('college_list')

@login_required
def college_detail(request, college_id):
    college = get_object_or_404(College, id=college_id)
    context = {
        'college': college
    }
    return render(request, 'recommendations/college_detail.html', context)