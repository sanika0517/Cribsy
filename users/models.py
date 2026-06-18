from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Choices for dropdown fields ---
GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

MARITAL_STATUS_CHOICES = (
    ('Single', 'Single'),
    ('Married', 'Married'),
    ('Divorced', 'Divorced'),
    ('Widowed', 'Widowed'),
)

RELIGION_CHOICES = (
    ('Hindu', 'Hindu'),
    ('Muslim', 'Muslim'),
    ('Christian', 'Christian'),
    ('Sikh', 'Sikh'),
    ('Other', 'Other'),
)

# --- Profile Model ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 🧍 Basic Info
    full_name = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    dob = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    # 📞 Contact Info
    phone = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True, help_text='Area/Locality within the city')
    state = models.CharField(max_length=100, blank=True)

    # 🎓 Education & Career
    qualification = models.CharField(max_length=150, blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    budget = models.PositiveIntegerField(null=True, blank=True, help_text='Monthly budget (INR)')

    # 🌸 Lifestyle & Preferences
    religion = models.CharField(max_length=100, choices=RELIGION_CHOICES, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, default='Single')
    hobbies = models.TextField(blank=True)
    lifestyle = models.TextField(blank=True)

    # 🖼 Profile Picture & Bio
    photo = models.ImageField(upload_to='profiles/', default='profiles/default.jpg')
    bio = models.TextField(blank=True)

    # 🪪 ID Proof
    id_proof = models.FileField(upload_to='id_proofs/', null=True, blank=True, help_text='Upload Aadhaar or other valid ID proof')

    # ✅ Verification
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    verification_status = models.CharField(
        max_length=10,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        help_text='Admin verification status'
    )
    verified = models.BooleanField(default=False, help_text='Legacy field - use verification_status')
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_profiles',
        help_text='Admin who verified this profile'
    )

    def save(self, *args, **kwargs):
        # Sync verified field with verification_status
        if self.verification_status == 'verified':
            self.verified = True
        else:
            self.verified = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.user.username


# --- Feedback/Review Model ---
class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.rating}/5"


# --- HomeSpace Model ---
class HomeSpace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='home_spaces')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    rent = models.PositiveIntegerField(null=True, blank=True, help_text='Monthly rent (INR)')
    available_from = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


# --- HomeSpace Photo Model ---
class HomeSpacePhoto(models.Model):
    home_space = models.ForeignKey(HomeSpace, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='home_spaces/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False, help_text='Primary photo for the space')
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']
    
    def __str__(self):
        return f"Photo for {self.home_space.title}"


# --- HomeSpace Review Model ---
class HomeSpaceReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    home_space = models.ForeignKey(HomeSpace, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='home_space_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['home_space', 'reviewer']  # One review per user per space
    
    def __str__(self):
        return f"{self.reviewer.username} - {self.rating}/5 for {self.home_space.title}"


# --- Auto-create or update profile when user registers ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()