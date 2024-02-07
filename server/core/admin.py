from django.contrib import admin

from rest_framework_api_key.admin import APIKeyModelAdmin

from contact.models import Contact
from core.models import Document, UserProfile, UserAPIKey, InviteCode
from stocks.models import Stock, Subscription


class UserAPIKeyModelAdmin(APIKeyModelAdmin):
    list_display = [*APIKeyModelAdmin.list_display, "user"]
    search_fields = [*APIKeyModelAdmin.search_fields, "user"]


class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "is_usable", "owner")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.save(user=request.user)
        else:
            obj.save()
        super().save_model(request, obj, form, change)


class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email")


admin.site.register(UserProfile)
admin.site.register(InviteCode, InviteCodeAdmin)
admin.site.register(UserAPIKey, UserAPIKeyModelAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Document)

admin.site.register(Stock)
admin.site.register(Subscription)
