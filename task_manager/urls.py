from django.urls import path

from . import views


urlpatterns = [
    path("", views.Index.as_view(), name="home"),
    path("tasks/", views.TaskListView.as_view(), name="task-list"),
    path("employees/", views.WorkerListView.as_view(), name="worker-list"),
    path("toggle-theme/", views.toggle_theme, name="toggle-theme"),
    path("sign-up/", views.SignUpView.as_view(), name="sign-up"),
]

app_name = "task_manager"
