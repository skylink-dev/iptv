from collections import defaultdict
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User, Group, Permission
from .models import UserProfile


# ==============================
# User & Profile Integration
# ==============================

class CustomUserChangeForm(UserChangeForm):
    """Custom User form with checkboxes for groups & permissions"""
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
        widgets = {
            "groups": forms.CheckboxSelectMultiple(),
            "user_permissions": forms.CheckboxSelectMultiple(),
        }


class UserProfileInline(admin.StackedInline):
    """Inline editor for UserProfile inside User admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    inlines = [UserProfileInline]

    list_display = ["username", "email", "get_role", "get_parent", "is_staff"]
    list_filter = ["is_staff", "is_superuser", "is_active", "groups", "profile__role"]
    search_fields = ["username", "email", "profile__role"]

    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, "profile") else "-"
    get_role.short_description = "Role"

    def get_parent(self, obj):
        return obj.profile.parent.user.username if hasattr(obj, "profile") and obj.profile.parent else "-"
    get_parent.short_description = "Parent"

    def save_model(self, request, obj, form, change):
        """Ensure UserProfile is created automatically"""
        super().save_model(request, obj, form, change)
        if not hasattr(obj, "profile"):
            UserProfile.objects.create(user=obj)


# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ==============================
# Custom Group Admin with Permission Grouping
# ==============================

class GroupAdminForm(forms.ModelForm):
    """Group form that groups permissions by app"""
    class Meta:
        model = Group
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        permissions = Permission.objects.select_related("content_type")
        grouped_permissions = defaultdict(list)

        for perm in permissions:
            module_name = perm.content_type.app_label.capitalize()
            grouped_permissions[module_name].append((perm.id, perm.name))

        # Replace default widget with checkbox grid
        self.fields["permissions"].widget = forms.CheckboxSelectMultiple()
        self.fields["permissions"].widget.attrs.update(
            {"class": "checkbox-grid permission-group"}
        )
        self.fields["permissions"].choices = [
            (module, perms) for module, perms in sorted(grouped_permissions.items())
        ]


class CustomGroupAdmin(GroupAdmin):
    form = GroupAdminForm
    list_display = ["name"]


# Replace default Group admin
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
