from typing import Optional
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import SignUpForm, TaskForm, WorkerPositionUpdateForm
from .models import Worker, Task, TaskType


class Index(LoginRequiredMixin, generic.ListView):
    model = Worker
    template_name = "task_manager/index.html"


def toggle_theme(request, **kwargs):
    if "is_dark_mode" in request.session:
        is_dark_mode = request.session.get("is_dark_mode")
        request.session["is_dark_mode"] = not is_dark_mode
    else:
        request.session["is_dark_mode"] = True
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task_manager:task-list")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm


class TaskDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView,
):
    model = Task
    success_url = reverse_lazy("task_manager:task-list")

    def test_func(self):
        return self.request.user.is_staff


@login_required
def toggle_task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    task.is_completed = not task.is_completed
    task.save()

    return redirect(task.get_absolute_url())


@login_required
def toggle_task_assign(request, pk):
    user = request.user
    task = get_object_or_404(Task, pk=pk)

    if task in user.tasks.all():
        user.tasks.remove(pk)
    else:
        user.tasks.add(pk)

    return redirect(task.get_absolute_url())


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    fields = ("name",)
    success_url = reverse_lazy("task_manager:task-type-list")


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskType
    fields = ("name",)
    success_url = reverse_lazy("task_manager:task-type-list")


class TaskTypeDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView,
):
    model = TaskType
    success_url = reverse_lazy("task_manager:task-type-list")

    def test_func(self):
        return self.request.user.is_staff


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker


class WorkerPositionUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView,
):
    model = Worker
    form_class = WorkerPositionUpdateForm
    success_url = reverse_lazy("task_manager:worker-list")

    def test_func(self):
        return self.request.user.is_staff


class WorkerDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView
):
    model = Worker
    success_url = reverse_lazy("task_manager:worker-list")

    def test_func(self):
        return self.request.user.is_staff


class SignUpView(generic.CreateView):
    model = Worker
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")
