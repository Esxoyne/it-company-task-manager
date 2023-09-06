from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import (
    SignUpForm,
    TaskForm,
    TaskRenewForm,
    WorkerUpdateForm,
    TaskSearchForm,
    TaskTypeSearchForm,
    WorkerSearchForm,
)
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
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        name = self.request.GET.get("name", "")
        context["search_form"] = TaskSearchForm(initial={
            "name": name,
        })
        return context

    def get_queryset(self):
        queryset = Task.objects.prefetch_related(
            "assignees"
        ).select_related("task_type")

        form = TaskSearchForm(self.request.GET)

        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )

        return queryset


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.prefetch_related(
        "assignees__position"
    ).select_related("task_type")


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task_manager:task-list")


class TaskUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView,
):
    model = Task
    form_class = TaskForm

    def test_func(self):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])

        return (
            self.request.user.is_staff
            or self.request.user in task.assignees.all()
        )


class TaskDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView,
):
    model = Task
    success_url = reverse_lazy("task_manager:task-list")

    def test_func(self):
        return self.request.user.is_staff


class TaskRenewView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView,
):
    model = Task
    form_class = TaskRenewForm

    def test_func(self):
        return (
            self.request.user.is_staff
            or self.request.user in self.get_object().assignees.all()
        )


class ToggleTaskCompleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.View,
):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])

        return redirect(task.get_absolute_url())

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])

        task.is_completed = not task.is_completed
        task.save()

        if self.request.POST["referer"] == "worker-detail":
            return redirect(self.request.user.get_absolute_url())
        elif self.request.POST["referer"] == "task-detail":
            return redirect(task.get_absolute_url())
        else:
            return redirect(reverse_lazy("task_manager:task-list"))

    def test_func(self):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])

        return (
            self.request.user.is_staff
            or self.request.user in task.assignees.all()
            and not task.is_overdue()
        )


class ToggleTaskAssignView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])

        return redirect(task.get_absolute_url())

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])
        user = request.user

        if user in task.assignees.all():
            task.assignees.remove(user)
        else:
            task.assignees.add(user)

        return redirect(task.get_absolute_url())


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        name = self.request.GET.get("name", "")
        context["search_form"] = TaskTypeSearchForm(initial={
            "name": name,
        })
        return context

    def get_queryset(self):
        queryset = TaskType.objects.prefetch_related("tasks")

        form = TaskTypeSearchForm(self.request.GET)

        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )

        return queryset


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
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        username = self.request.GET.get("username", "")
        context["search_form"] = WorkerSearchForm(initial={
            "username": username,
        })
        return context

    def get_queryset(self):
        queryset = Worker.objects.prefetch_related(
            "tasks"
        ).select_related("position")

        form = WorkerSearchForm(self.request.GET)

        if form.is_valid():
            return queryset.filter(
                username__icontains=form.cleaned_data["username"]
            )

        return queryset


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_tasks = self.object.tasks.prefetch_related(
            "assignees"
        ).select_related("task_type")

        context["completed_tasks"] = all_tasks.filter(
            is_completed=True,
        )

        context["incomplete_tasks"] = all_tasks.filter(
            is_completed=False,
        )

        context["worker_is_user"] = self.object == self.request.user

        return context


class WorkerUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView,
):
    model = Worker
    form_class = WorkerUpdateForm

    def test_func(self):
        return self.request.user.is_staff or (
            self.get_object().pk == self.request.user.pk
        )


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
