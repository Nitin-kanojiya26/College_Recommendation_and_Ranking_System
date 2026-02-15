from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.shortcuts import render
from .views import edit_profile
from .views import logout_view
from .views import (
    StudentViewSet, 
    CollegeViewSet, 
    GenerateRecommendationsView,
    FilterRecommendationsView,
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    CurrentUserView,
    UpdateStudentProfileView,
    home,
    student_dashboard,
    college_list,
    generate_recommendations_page,
    login_user,          # Changed from login_page to login_user
    register_user,       # Changed from register_page to register_user
    profile_page,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'colleges', CollegeViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', student_dashboard, name='dashboard'),
    path('colleges/', college_list, name='college_list'),
    path('generate/', generate_recommendations_page, name='generate_recommendations_page'),
    
    # **CHANGED: Web form authentication endpoints (handle POST requests)**
    path('register/', register_user, name='register'),      # Now uses register_user (handles POST)
    path('login/', login_user, name='login'),              # Now uses login_user (handles POST)
    path('profile/', profile_page, name='profile_page'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('logout/', logout_view, name='logout'),
    # API endpoints (for JavaScript/frontend apps)
    path('api/', include(router.urls)),
    path('api/auth/register/', UserRegistrationView.as_view(), name='api_register'),   # Added 'api_' prefix
    path('api/auth/login/', UserLoginView.as_view(), name='api_login'),                # Added 'api_' prefix
    path('api/auth/logout/', UserLogoutView.as_view(), name='api_logout'),
    path('api/auth/me/', CurrentUserView.as_view(), name='api_current_user'),
    path('api/auth/profile/update/', UpdateStudentProfileView.as_view(), name='api_update_profile'),
    path('api/generate-recommendations/', GenerateRecommendationsView.as_view(), 
         name='generate_recommendations'),
    path('api/filter-recommendations/', FilterRecommendationsView.as_view(), 
         name='filter_recommendations'),
]