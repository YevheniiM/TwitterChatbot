from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import TwitterMonitoring, Friends


class TwitterMonitoringForm(forms.ModelForm):
    class Meta:
        model = TwitterMonitoring
        fields = ('twitter_handle', 'check_rate', 'telegram_channel')


class TwitterMonitoringAdmin(admin.ModelAdmin):
    form = TwitterMonitoringForm
    list_display = ('twitter_handle', 'check_rate')
    search_fields = ('twitter_handle',)

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
