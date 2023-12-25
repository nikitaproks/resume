from django.contrib import admin

from contact.models import Contact
from core.models import Document


class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email")


admin.site.register(Contact, ContactAdmin)
admin.site.register(Document)
