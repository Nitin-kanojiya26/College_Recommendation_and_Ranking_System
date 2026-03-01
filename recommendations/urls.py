from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('colleges/', views.college_list, name='college_list'),
    path('college/<int:college_id>/', views.college_detail, name='college_detail'),
    path('generate/', views.generate_recommendations, name='generate_recommendations'),
    path('save-college/', views.save_college, name='save_college'),
    path('save-dashboard-preferences/', views.save_dashboard_preferences, name='save_dashboard_preferences'),
]