from django.db import models
from django.contrib.auth.models import User

class Swipe(models.Model):
    swiper = models.ForeignKey(User, related_name='swipes_made', on_delete=models.CASCADE)
    swiped = models.ForeignKey(User, related_name='swiped_by', on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('swiper', 'swiped')

    def __str__(self):
        return f"{self.swiper.username} -> {self.swiped.username} ({'liked' if self.liked else 'skipped'})"

class ConnectionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"

class Match(models.Model):
    user1 = models.ForeignKey(User, related_name='matches_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='matches_user2', on_delete=models.CASCADE)
    matched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Match: {self.user1.username} & {self.user2.username}"
