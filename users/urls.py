from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search, name='search'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_dashboard/verify/<int:profile_id>/', views.verify_profile, name='verify_profile'),
    path('admin_dashboard/reject/<int:profile_id>/', views.reject_profile, name='reject_profile'),
    path('admin_dashboard/delete-fake/<int:profile_id>/', views.delete_fake_profile, name='delete_fake_profile'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # ✅ Profile routes
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('my-profile/', views.my_profile, name='my_profile'),
    
    # 🏠 Home Spaces routes
    path('home-spaces/', views.home_spaces_list, name='home_spaces_list'),
    path('home-spaces/add/', views.add_home_space, name='add_home_space'),
    path('home-spaces/<int:space_id>/', views.home_space_detail, name='home_space_detail'),
    path('home-spaces/<int:space_id>/edit/', views.edit_home_space, name='edit_home_space'),
    path('home-spaces/photo/<int:photo_id>/delete/', views.delete_home_space_photo, name='delete_home_space_photo'),
    path('my-home-spaces/', views.my_home_spaces, name='my_home_spaces'),
]