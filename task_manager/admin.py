from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import Position, Project, Task, TaskType, Worker


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position",)
    fieldsets = UserAdmin.fieldsets + (
        (("Additional info", {"fields": ("position",)}),)
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "position",
                )
            },
        ),
    )
    list_filter = ("position",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ("name", "description")
    list_filter = (
        "is_completed",
        "priority",
        "task_type",
        "assignees",
        "project",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("members",)


admin.site.register(Position)
admin.site.register(TaskType)
admin.site.unregister(Group)
