from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Feedback, HomeSpace, HomeSpacePhoto, HomeSpaceReview

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'verification_status_badge', 'city', 'phone', 'id_proof_link', 'created_at']
    list_filter = ['verification_status', 'verified', 'city', 'state']
    search_fields = ['user__username', 'user__email', 'full_name', 'phone', 'city']
    readonly_fields = ['verified_at', 'verified_by']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Basic Information', {
            'fields': ('full_name', 'gender', 'dob', 'age', 'photo', 'bio')
        }),
        ('Contact Information', {
            'fields': ('phone', 'city', 'state')
        }),
        ('Education & Career', {
            'fields': ('qualification', 'occupation', 'budget')
        }),
        ('Lifestyle', {
            'fields': ('religion', 'marital_status', 'hobbies', 'lifestyle')
        }),
        ('Verification', {
            'fields': ('id_proof', 'verification_status', 'verified', 'verified_at', 'verified_by')
        }),
    )
    
    def verification_status_badge(self, obj):
        colors = {
            'verified': '#10b981',
            'pending': '#f59e0b',
            'rejected': '#ef4444'
        }
        color = colors.get(obj.verification_status, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{}</span>',
            color,
            obj.get_verification_status_display()
        )
    verification_status_badge.short_description = 'Status'
    
    def id_proof_link(self, obj):
        if obj.id_proof:
            return format_html('<a href="{}" target="_blank">View ID Proof</a>', obj.id_proof.url)
        return format_html('<span style="color: #ef4444;">No ID Proof</span>')
    id_proof_link.short_description = 'ID Proof'
    
    def created_at(self, obj):
        return obj.user.date_joined.strftime('%Y-%m-%d')
    created_at.short_description = 'Joined'
    
    actions = ['verify_selected_profiles', 'reject_and_delete_selected_profiles']
    
    def verify_selected_profiles(self, request, queryset):
        """Admin action to verify selected profiles"""
        from django.utils import timezone
        count = 0
        for profile in queryset:
            profile.verification_status = 'verified'
            profile.verified = True
            profile.verified_at = timezone.now()
            profile.verified_by = request.user
            profile.save()
            count += 1
        self.message_user(request, f'{count} profile(s) have been verified.')
    verify_selected_profiles.short_description = '✓ Verify selected profiles'
    
    def reject_and_delete_selected_profiles(self, request, queryset):
        """Admin action to reject and delete selected profiles"""
        count = 0
        for profile in queryset:
            username = profile.user.username
            profile.user.delete()  # Cascade will delete profile
            count += 1
        self.message_user(request, f'{count} profile(s) have been rejected and accounts deleted.', level='ERROR')
    reject_and_delete_selected_profiles.short_description = '✗ Reject & Delete selected profiles'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating_display', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'user__email', 'comment']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="font-size: 1.1rem;">{}</span>', stars)
    rating_display.short_description = 'Rating'
    
    def comment_preview(self, obj):
        if obj.comment:
            preview = obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
            return preview
        return '-'
    comment_preview.short_description = 'Comment'


@admin.register(HomeSpace)
class HomeSpaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'city', 'rent', 'created_at', 'photo_count']
    list_filter = ['city', 'state', 'created_at']
    search_fields = ['title', 'description', 'address', 'city', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'


@admin.register(HomeSpacePhoto)
class HomeSpacePhotoAdmin(admin.ModelAdmin):
    list_display = ['home_space', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['home_space__title', 'caption']


@admin.register(HomeSpaceReview)
class HomeSpaceReviewAdmin(admin.ModelAdmin):
    list_display = ['home_space', 'reviewer', 'rating_display', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['home_space__title', 'reviewer__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="font-size: 1.1rem;">{}</span>', stars)
    rating_display.short_description = 'Rating'
