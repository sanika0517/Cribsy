from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .forms import SignUpForm, ProfileForm, FeedbackForm, HomeSpaceForm, HomeSpaceReviewForm
from .models import Profile, Feedback, HomeSpace, HomeSpacePhoto, HomeSpaceReview
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from matches.models import Match, ConnectionRequest

# Home Page
def home(request):
    # Fetch recent feedback with user profiles (only feedback with comments)
    feedbacks = Feedback.objects.filter(
        comment__isnull=False
    ).exclude(
        comment=''
    ).select_related('user', 'user__profile').order_by('-created_at')[:6]
    
    return render(request, 'users/index.html', {
        'feedbacks': feedbacks
    })

# User Signup
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, "Account created successfully! Please log in.")
                return redirect('login')  # redirect to login after signup
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            # Form validation errors will be displayed in template
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    
    return render(request, 'users/signup.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # ✅ Redirect to home page after login
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    # ✅ Redirect to home after logout
    return redirect('index')

# Admin Dashboard
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    from django.db.models import Q
    
    # Get all profiles with their users, EXCLUDING superuser/admin accounts
    profiles = Profile.objects.select_related('user', 'verified_by').filter(
        user__is_superuser=False
    ).order_by('-user__date_joined')
    
    # Filter by verification status
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'pending':
        profiles = profiles.filter(verification_status='pending')
    elif status_filter == 'verified':
        profiles = profiles.filter(verification_status='verified')
    elif status_filter == 'rejected':
        profiles = profiles.filter(verification_status='rejected')
    
    # Stats (excluding superusers)
    regular_profiles = Profile.objects.filter(user__is_superuser=False)
    stats = {
        'total': regular_profiles.count(),
        'pending': regular_profiles.filter(verification_status='pending').count(),
        'verified': regular_profiles.filter(verification_status='verified').count(),
        'rejected': regular_profiles.filter(verification_status='rejected').count(),
    }
    
    return render(request, 'users/admin_dashboard.html', {
        'profiles': profiles,
        'stats': stats,
        'current_filter': status_filter
    })

# Admin Actions
@user_passes_test(lambda u: u.is_superuser)
def verify_profile(request, profile_id):
    """Admin verifies a profile"""
    from django.utils import timezone
    profile = get_object_or_404(Profile, id=profile_id)
    profile.verification_status = 'verified'
    profile.verified = True
    profile.verified_at = timezone.now()
    profile.verified_by = request.user
    profile.save()
    messages.success(request, f"Profile for {profile.user.username} has been verified!")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def reject_profile(request, profile_id):
    """Admin rejects a profile and deletes the user account"""
    profile = get_object_or_404(Profile, id=profile_id)
    username = profile.user.username
    # Delete user account (cascade will delete profile and all related data)
    profile.user.delete()
    messages.error(request, f"Profile for {username} has been rejected and the account has been deleted.")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_fake_profile(request, profile_id):
    """Admin deletes a fake profile and its user account"""
    profile = get_object_or_404(Profile, id=profile_id)
    username = profile.user.username
    # Delete user (cascade will delete profile)
    profile.user.delete()
    messages.error(request, f"Account for {username} has been deleted due to fake profile.")
    return redirect('admin_dashboard')

# Delete a User (admin only) - Legacy
@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f"User {username} has been deleted.")
    return redirect('admin_dashboard')

# Search for flatmates
@login_required
def search(request):
    q_area = request.GET.get('area', '').strip()
    q_gender = request.GET.get('gender', '')
    q_budget = request.GET.get('budget', '')
    qs = Profile.objects.exclude(user=request.user).select_related('user')

    if q_area:
        qs = qs.filter(area__icontains=q_area)
    if q_gender:
        qs = qs.filter(gender=q_gender)
    if q_budget:
        try:
            b = int(q_budget)
            qs = qs.filter(budget__lte=b)
        except:
            pass
    
    # Get request statuses for each profile
    profiles_with_status = []
    for profile in qs:
        # Check if already matched
        is_matched = Match.objects.filter(
            (Q(user1=request.user) & Q(user2=profile.user)) |
            (Q(user1=profile.user) & Q(user2=request.user))
        ).exists()
        
        # Check for pending requests
        sent_request = ConnectionRequest.objects.filter(
            sender=request.user,
            receiver=profile.user,
            status='pending'
        ).first()
        
        received_request = ConnectionRequest.objects.filter(
            sender=profile.user,
            receiver=request.user,
            status='pending'
        ).first()
        
        profiles_with_status.append({
            'profile': profile,
            'is_matched': is_matched,
            'sent_request': sent_request,
            'received_request': received_request
        })
    
    return render(request, 'users/search.html', {'profiles_data': profiles_with_status})

# Dashboard
@login_required
def dashboard(request):
    from matches.models import ConnectionRequest, Match
    from chat.models import Message
    from django.db.models import Q
    
    # Get user profile
    profile = getattr(request.user, 'profile', None)
    
    # Get pending connection requests
    pending_requests = ConnectionRequest.objects.filter(
        receiver=request.user,
        status='pending'
    ).select_related('sender', 'sender__profile')[:5]
    
    # Get recent matches/connections
    matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2', 'user1__profile', 'user2__profile')
    
    connections = []
    for match in matches:
        partner = match.user2 if match.user1 == request.user else match.user1
        # Get last message with this partner
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=partner)) |
            (Q(sender=partner) & Q(receiver=request.user))
        ).order_by('-timestamp').first()
        
        connections.append({
            'user': partner,
            'last_message': last_message,
            'matched_at': match.matched_at
        })
    
    # Handle feedback submission
    feedback_form = FeedbackForm()
    if request.method == 'POST' and 'submit_feedback' in request.POST:
        feedback_form = FeedbackForm(request.POST)
        if feedback_form.is_valid():
            feedback = feedback_form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('dashboard')
    
    # Get user's recent feedback
    user_feedback = Feedback.objects.filter(user=request.user).first()
    
    return render(request, 'users/dashboard.html', {
        'profile': profile,
        'pending_requests': pending_requests,
        'connections': connections,
        'feedback_form': feedback_form,
        'user_feedback': user_feedback,
    })

# My Profile (View own profile)
@login_required
def my_profile(request):
    profile = request.user.profile
    context = {
        'profile': profile,
        'can_edit': True,
    }
    return render(request, 'users/view_profile.html', context)

# Create/Edit Profile
@login_required
def create_profile(request):
    """Allow logged-in users to create their profile only once."""
    # If profile already exists → redirect to edit page
    if hasattr(request.user, 'profile'):
        return redirect('edit_profile', username=request.user.username)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile created successfully!")
            return redirect('my_profile')
    else:
        form = ProfileForm()

    return render(request, 'users/create_profile.html', {'form': form})

# Edit Profile (same as above, optional)
@login_required
def edit_profile(request, username):
    if username != request.user.username:
        return HttpResponseForbidden("You can only edit your own profile.")

    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/profile_form.html', {'form': form})

@login_required
def view_profile(request, username):
    """View another user's profile by username."""
    user_obj = get_object_or_404(User, username=username)
    profile = getattr(user_obj, 'profile', None)
    can_edit = bool(profile and request.user.is_authenticated and profile.user == request.user)
    return render(
        request,
        'users/view_profile.html',
        {
            'user_obj': user_obj,
            'profile': profile,
            'can_edit': can_edit,
        },
    )


# ========== Home Spaces Views ==========

def home_spaces_list(request):
    """List all home spaces"""
    spaces = HomeSpace.objects.select_related('user', 'user__profile').prefetch_related('photos').all()
    
    # Filter by city if provided
    city_filter = request.GET.get('city', '')
    if city_filter:
        spaces = spaces.filter(city__icontains=city_filter)
    
    # Calculate average ratings
    from django.db.models import Avg
    spaces_with_ratings = []
    for space in spaces:
        avg_rating = space.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        spaces_with_ratings.append({
            'space': space,
            'avg_rating': round(avg_rating, 1),
            'review_count': space.reviews.count(),
            'primary_photo': space.photos.filter(is_primary=True).first() or space.photos.first()
        })
    
    return render(request, 'users/home_spaces_list.html', {
        'spaces_with_ratings': spaces_with_ratings,
        'city_filter': city_filter,
    })


def home_space_detail(request, space_id):
    """View details of a specific home space"""
    space = get_object_or_404(HomeSpace.objects.select_related('user', 'user__profile'), id=space_id)
    photos = space.photos.all()
    reviews = space.reviews.select_related('reviewer', 'reviewer__profile').all()
    
    # Calculate average rating
    from django.db.models import Avg
    avg_rating = space.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()
    
    # Check if user has already reviewed
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(reviewer=request.user).first()
    
    # Check connection status with owner
    is_matched = False
    sent_request = None
    received_request = None
    if request.user.is_authenticated and space.user != request.user:
        is_matched = Match.objects.filter(
            (Q(user1=request.user) & Q(user2=space.user)) |
            (Q(user1=space.user) & Q(user2=request.user))
        ).exists()
        
        if not is_matched:
            sent_request = ConnectionRequest.objects.filter(
                sender=request.user,
                receiver=space.user,
                status='pending'
            ).first()
            
            received_request = ConnectionRequest.objects.filter(
                sender=space.user,
                receiver=request.user,
                status='pending'
            ).first()
    
    # Review form (only for authenticated users)
    review_form = None
    if request.user.is_authenticated:
        if request.method == 'POST' and 'submit_review' in request.POST:
            if user_review:
                review_form = HomeSpaceReviewForm(request.POST, instance=user_review)
            else:
                review_form = HomeSpaceReviewForm(request.POST)
            
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.home_space = space
                review.reviewer = request.user
                review.save()
                messages.success(request, "Review submitted successfully!")
                return redirect('home_space_detail', space_id=space_id)
        else:
            if user_review:
                review_form = HomeSpaceReviewForm(instance=user_review)
            else:
                review_form = HomeSpaceReviewForm()
    
    return render(request, 'users/home_space_detail.html', {
        'space': space,
        'photos': photos,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
        'user_review': user_review,
        'review_form': review_form,
        'is_matched': is_matched,
        'sent_request': sent_request,
        'received_request': received_request,
    })


@login_required
def add_home_space(request):
    """Add a new home space"""
    if request.method == 'POST':
        form = HomeSpaceForm(request.POST)
        if form.is_valid():
            space = form.save(commit=False)
            space.user = request.user
            space.save()
            
            # Handle photo uploads
            photos = request.FILES.getlist('photos')
            if photos:
                for i, photo in enumerate(photos):
                    HomeSpacePhoto.objects.create(
                        home_space=space,
                        photo=photo,
                        is_primary=(i == 0)  # First photo is primary
                    )
            
            messages.success(request, "Home space added successfully!")
            return redirect('home_space_detail', space_id=space.id)
    else:
        form = HomeSpaceForm()
    
    return render(request, 'users/add_home_space.html', {'form': form})


@login_required
def edit_home_space(request, space_id):
    """Edit a home space"""
    space = get_object_or_404(HomeSpace, id=space_id)
    
    # Only owner can edit
    if space.user != request.user:
        messages.error(request, "You don't have permission to edit this space.")
        return redirect('home_space_detail', space_id=space_id)
    
    if request.method == 'POST':
        form = HomeSpaceForm(request.POST, instance=space)
        if form.is_valid():
            form.save()
            
            # Handle new photo uploads
            photos = request.FILES.getlist('photos')
            if photos:
                for photo in photos:
                    HomeSpacePhoto.objects.create(
                        home_space=space,
                        photo=photo
                    )
            
            messages.success(request, "Home space updated successfully!")
            return redirect('home_space_detail', space_id=space_id)
    else:
        form = HomeSpaceForm(instance=space)
    
    existing_photos = space.photos.all()
    return render(request, 'users/edit_home_space.html', {
        'form': form,
        'space': space,
        'existing_photos': existing_photos,
    })


@login_required
def delete_home_space_photo(request, photo_id):
    """Delete a photo from a home space"""
    photo = get_object_or_404(HomeSpacePhoto, id=photo_id)
    space = photo.home_space
    
    # Only owner can delete
    if space.user != request.user:
        messages.error(request, "You don't have permission to delete this photo.")
        return redirect('home_space_detail', space_id=space.id)
    
    photo.delete()
    messages.success(request, "Photo deleted successfully!")
    return redirect('edit_home_space', space_id=space.id)


@login_required
def my_home_spaces(request):
    """View user's own home spaces"""
    spaces = HomeSpace.objects.filter(user=request.user).prefetch_related('photos', 'reviews')
    return render(request, 'users/my_home_spaces.html', {'spaces': spaces})