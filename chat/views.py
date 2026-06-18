from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import MessageForm
from .models import Message
from matches.models import Match
from django.db.models import Q

@login_required
def conversations(request):
    matches = Match.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    partners = []
    for m in matches:
        partner = m.user2 if m.user1 == request.user else m.user1
        partners.append(partner)
    return render(request, 'chat/conversations.html', {'partners': partners})

@login_required
def conversation_view(request, username):
    partner = get_object_or_404(User, username=username)
    matched = Match.objects.filter(
        (Q(user1=request.user) & Q(user2=partner)) | (Q(user1=partner) & Q(user2=request.user))
    ).exists()
    if not matched:
        return redirect('conversations')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = partner
            msg.save()
            return redirect('conversation', username=username)
    else:
        form = MessageForm()
    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=partner) | Q(sender=partner, receiver=request.user))).order_by('timestamp')
    return render(request, 'chat/conversation.html', {'partner': partner, 'messages': messages, 'form': form})
