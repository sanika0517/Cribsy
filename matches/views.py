from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Swipe, Match, ConnectionRequest
from django.contrib.auth.models import User

@login_required
def swipe_view(request):
    swiped_ids = Swipe.objects.filter(swiper=request.user).values_list('swiped_id', flat=True)
    candidates = User.objects.exclude(id__in=swiped_ids).exclude(id=request.user.id).select_related('profile')
    candidate = candidates.first()
    return render(request, 'matches/swipe.html', {'candidate': candidate})

@login_required
def swipe_action(request, swiped_id):
    if request.method == 'POST':
        liked = request.POST.get('like') == 'true'
        swiped_user = get_object_or_404(User, id=swiped_id)
        swipe, created = Swipe.objects.get_or_create(swiper=request.user, swiped=swiped_user)
        swipe.liked = liked
        swipe.save()

        if liked:
            reverse = Swipe.objects.filter(swiper=swiped_user, swiped=request.user, liked=True).first()
            if reverse:
                u1, u2 = sorted([request.user, swiped_user], key=lambda u: u.id)
                Match.objects.get_or_create(user1=u1, user2=u2)
        return redirect('swipe')
    return redirect('swipe')

# Connection Request Views
@login_required
def send_request(request, user_id):
    """Send a connection request to another user"""
    receiver = get_object_or_404(User, id=user_id)
    
    if receiver == request.user:
        messages.error(request, "You cannot send a request to yourself.")
        return redirect('search')
    
    # Check if request already exists
    existing_request = ConnectionRequest.objects.filter(
        sender=request.user,
        receiver=receiver
    ).first()
    
    if existing_request:
        if existing_request.status == 'pending':
            messages.info(request, f"You already have a pending request with {receiver.username}.")
        elif existing_request.status == 'accepted':
            messages.info(request, f"You are already connected with {receiver.username}.")
        else:
            # Resend rejected request
            existing_request.status = 'pending'
            existing_request.save()
            messages.success(request, f"Connection request sent to {receiver.username}!")
    else:
        # Check if already matched
        is_matched = Match.objects.filter(
            (Q(user1=request.user) & Q(user2=receiver)) |
            (Q(user1=receiver) & Q(user2=request.user))
        ).exists()
        
        if is_matched:
            messages.info(request, f"You are already connected with {receiver.username}.")
        else:
            ConnectionRequest.objects.create(sender=request.user, receiver=receiver)
            messages.success(request, f"Connection request sent to {receiver.username}!")
    
    return redirect('search')

@login_required
def accept_request(request, request_id):
    """Accept a connection request"""
    connection_request = get_object_or_404(
        ConnectionRequest,
        id=request_id,
        receiver=request.user,
        status='pending'
    )
    
    connection_request.status = 'accepted'
    connection_request.save()
    
    # Create a Match
    u1, u2 = sorted([connection_request.sender, connection_request.receiver], key=lambda u: u.id)
    Match.objects.get_or_create(user1=u1, user2=u2)
    
    messages.success(request, f"You are now connected with {connection_request.sender.username}!")
    return redirect('requests')

@login_required
def reject_request(request, request_id):
    """Reject a connection request"""
    connection_request = get_object_or_404(
        ConnectionRequest,
        id=request_id,
        receiver=request.user,
        status='pending'
    )
    
    connection_request.status = 'rejected'
    connection_request.save()
    
    messages.info(request, f"Request from {connection_request.sender.username} has been rejected.")
    return redirect('requests')

@login_required
def cancel_request(request, request_id):
    """Cancel a sent request"""
    connection_request = get_object_or_404(
        ConnectionRequest,
        id=request_id,
        sender=request.user,
        status='pending'
    )
    
    connection_request.delete()
    messages.info(request, "Request cancelled.")
    return redirect('requests')

@login_required
def requests_view(request):
    """View all connection requests (sent and received)"""
    sent_requests = ConnectionRequest.objects.filter(
        sender=request.user,
        status='pending'
    ).select_related('receiver', 'receiver__profile')
    
    received_requests = ConnectionRequest.objects.filter(
        receiver=request.user,
        status='pending'
    ).select_related('sender', 'sender__profile')
    
    # Get all matches/connections
    matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2', 'user1__profile', 'user2__profile')
    
    connections = []
    for match in matches:
        partner = match.user2 if match.user1 == request.user else match.user1
        connections.append({
            'user': partner,
            'matched_at': match.matched_at
        })
    
    return render(request, 'matches/requests.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests,
        'connections': connections
    })
