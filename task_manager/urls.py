from django.urls import path

from . import views


urlpatterns = [
    path("", views.Index.as_view(), name="home"),
    path("tasks/", views.TaskListView.as_view(), name="task-list"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="task-create"),
    path(
        "tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"
    ),
    path(
        "tasks/<int:pk>/update/",
        views.TaskUpdateView.as_view(),
        name="task-update",
    ),
    path(
        "tasks/<int:pk>/delete/",
        views.TaskDeleteView.as_view(),
        name="task-delete",
    ),
    path(
        "tasks/<int:pk>/toggle-complete/",
        views.toggle_task_complete,
        name="toggle-task-complete",
    ),
    path(
        "tasks/<int:pk>/toggle-assign/",
        views.toggle_task_assign,
        name="toggle-task-assign",
    ),
    path(
        "task-types/",
        views.TaskTypeListView.as_view(),
        name="task-type-list",
    ),
    path(
        "task-types/create/",
        views.TaskTypeCreateView.as_view(),
        name="task-type-create"
    ),
    path(
        "task-types/<int:pk>/update/",
        views.TaskTypeUpdateView.as_view(),
        name="task-type-update"
    ),
    path(
        "task-types/<int:pk>/delete/",
        views.TaskTypeDeleteView.as_view(),
        name="task-type-delete"
    ),
    path("team/", views.WorkerListView.as_view(), name="worker-list"),
    path(
        "team/<int:pk>/",
        views.WorkerDetailView.as_view(),
        name="worker-detail",
    ),
    path(
        "team/<int:pk>/update/",
        views.WorkerUpdateView.as_view(),
        name="worker-update",
    ),
    path(
        "team/<int:pk>/delete/",
        views.WorkerDeleteView.as_view(),
        name="worker-delete",
    ),
    path("toggle-theme/", views.toggle_theme, name="toggle-theme"),
    path("sign-up/", views.SignUpView.as_view(), name="sign-up"),
]

app_name = "task_manager"
