from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import TwitterMonitoring, Friends


class TwitterMonitoringForm(forms.ModelForm):
    class Meta:
        model = TwitterMonitoring
        fields = ('twitter_handle', 'check_rate', 'telegram_channel')


class TwitterMonitoringAdmin(admin.ModelAdmin):
    list_display = ('twitter_handle', 'check_rate', 'telegram_channel', 'friend_count')
    search_fields = ('twitter_handle',)

    def friend_count(self, obj):
        return obj.friends.count()
    friend_count.short_description = 'Followings Count'

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            messages.error(request, str(e))


class FriendsAdmin(admin.ModelAdmin):
    pass


admin.site.register(TwitterMonitoring, TwitterMonitoringAdmin)
admin.site.register(Friends, FriendsAdmin)
