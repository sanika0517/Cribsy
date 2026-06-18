from django.urls import path
from . import views

urlpatterns = [
    path('swipe/', views.swipe_view, name='swipe'),
    path('swipe/<int:swiped_id>/', views.swipe_action, name='swipe_action'),
    # Connection Request URLs
    path('send-request/<int:user_id>/', views.send_request, name='send_request'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('cancel-request/<int:request_id>/', views.cancel_request, name='cancel_request'),
    path('requests/', views.requests_view, name='requests'),
]
