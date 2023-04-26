from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        print('!!!!>    ' * 10, flush=True)
        extra_context['custom_instructions_link'] = format_html(
            '<a href="{}" class="button">Custom Instructions</a>',
            reverse('custom_instructions')
        )
        return super().index(request, extra_context=extra_context)


custom_admin_site = CustomAdminSite(name='custom_admin')
