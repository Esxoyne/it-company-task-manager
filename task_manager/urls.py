from django.urls import path

from . import views


urlpatterns = [
    path("", views.Index.as_view(), name="home"),
    path("tasks/", views.TaskListView.as_view(), name="task-list"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="task-create"),
    path(
        "tasks/<int:pk>/",
        views.TaskDetailView.as_view(),
        name="task-detail",
    ),
    path(
        "tasks/<int:pk>/update/",
        views.TaskUpdateView.as_view(),
        name="task-update",
    ),
    path(
        "tasks/<int:pk>/renew/",
        views.TaskRenewView.as_view(),
        name="task-renew",
    ),
    path(
        "tasks/<int:pk>/delete/",
        views.TaskDeleteView.as_view(),
        name="task-delete",
    ),
    path(
        "tasks/<int:pk>/toggle-complete/",
        views.TaskToggleCompleteView.as_view(),
        name="task-toggle-complete",
    ),
    path(
        "tasks/<int:pk>/toggle-assign/",
        views.TaskToggleAssignView.as_view(),
        name="task-toggle-assign",
    ),
    path(
        "task-types/",
        views.TaskTypeListView.as_view(),
        name="task-type-list",
    ),
    path(
        "task-types/create/",
        views.TaskTypeCreateView.as_view(),
        name="task-type-create",
    ),
    path(
        "task-types/<int:pk>/update/",
        views.TaskTypeUpdateView.as_view(),
        name="task-type-update",
    ),
    path(
        "task-types/<int:pk>/delete/",
        views.TaskTypeDeleteView.as_view(),
        name="task-type-delete",
    ),
    path(
        "positions/",
        views.PositionListView.as_view(),
        name="position-list",
    ),
    path(
        "positions/create/",
        views.PositionCreateView.as_view(),
        name="position-create",
    ),
    path(
        "positions/<int:pk>/update/",
        views.PositionUpdateView.as_view(),
        name="position-update",
    ),
    path(
        "positions/<int:pk>/delete/",
        views.PositionDeleteView.as_view(),
        name="position-delete",
    ),
    path(
        "projects/",
        views.ProjectListView.as_view(),
        name="project-list",
    ),
    path(
        "projects/create/",
        views.ProjectCreateView.as_view(),
        name="project-create",
    ),
    path(
        "projects/<int:pk>/",
        views.ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path(
        "projects/<int:pk>/update/",
        views.ProjectUpdateView.as_view(),
        name="project-update",
    ),
    path(
        "projects/<int:pk>/delete/",
        views.ProjectDeleteView.as_view(),
        name="project-delete",
    ),
    path(
        "projects/<int:pk>/toggle-join/",
        views.ProjectToggleJoinView.as_view(),
        name="project-toggle-join",
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
