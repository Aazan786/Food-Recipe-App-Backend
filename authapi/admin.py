from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class MyUserModeladmin(UserAdmin):
    list_display = ('id', 'email', 'name', 'tc', 'is_active', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ('name', 'tc')}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name","tc", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []




admin.site.register(User, MyUserModeladmin)


