from django.contrib import admin
from .models import Progress, Subscription

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'sign_name', 'completed', 'completed_at', 'practice_count')
    list_filter = ('completed', 'sign_name')
    search_fields = ('user__username', 'sign_name')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('plan', 'is_active')
    search_fields = ('user__username', 'transaction_id')