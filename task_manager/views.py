import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import (
    ProjectForm,
    ProjectTaskAddForm,
    SignUpForm,
    TaskCreateForm,
    TaskUpdateForm,
    TaskRenewForm,
    TaskFilterForm,
    WorkerFilterForm,
    WorkerUpdateForm,
    NameSearchForm,
    WorkerSearchForm,
)
from .models import Worker, Task, TaskType, Position, Project


class Index(LoginRequiredMixin, generic.DetailView):
    template_name = "task_manager/index.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tasks = self.object.tasks.all()
        projects = self.object.projects.all()

        if tasks:
            if tasks.filter(is_completed=False):
                next_task = tasks.filter(
                    is_completed=False
                ).latest("-deadline")
            else:
                next_task = tasks.latest("deadline")
        else:
            next_task = None

        latest_project = projects.last()

        context["tasks"] = tasks
        if next_task:
            context["next_task"] = next_task

        context["completed_task_count"] = tasks.filter(
            is_completed=True
        ).count()
        context["overdue_task_count"] = len(
            [task for task in tasks if task.is_overdue]
        )

        uncompleted_tasks = tasks.filter(is_completed=False)
        current_week = datetime.date.today().isocalendar()[1]
        context["tasks_this_week"] = uncompleted_tasks.filter(
            deadline__week=current_week,
        ).count()

        context["projects"] = projects
        context["project_count"] = projects.count()

        if latest_project:
            context["latest_project"] = latest_project
            context["latest_project_completed_tasks_count"] = (
                latest_project.tasks.filter(is_completed=True).count()
            )

        context["team_members_count"] = Worker.objects.count()

        return context


class ToggleTheme(generic.View):
    def get(self, request, *args, **kwargs):
        is_dark_mode = request.session.get("is_dark_mode", False)
        request.session["is_dark_mode"] = not is_dark_mode
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class PassRequestToFormViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        name = self.request.GET.get("name", "")
        context["search_form"] = NameSearchForm(initial={
            "name": name,
        })

        project = self.request.GET.get("project", "")
        task_type = self.request.GET.get("task_type", "")
        context["filter_form"] = TaskFilterForm(initial={
            "project": project,
            "task_type": task_type,
        })

        return context

    def get_queryset(self):
        queryset = Task.objects.prefetch_related(
            "assignees"
        ).select_related("task_type")

        search_form = NameSearchForm(self.request.GET)
        filter_form = TaskFilterForm(self.request.GET)

        if search_form.is_valid():
            queryset = queryset.filter(
                name__icontains=search_form.cleaned_data["name"]
            )

        if filter_form.is_valid():
            for field, value in filter_form.cleaned_data.items():
                if value:
                    queryset = queryset.filter(**{field: value})

            return queryset

        return queryset


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.prefetch_related(
        "assignees__position"
    ).select_related("task_type")


class TaskCreateView(
    LoginRequiredMixin,
    PassRequestToFormViewMixin,
    generic.CreateView,
):
    model = Task
    form_class = TaskCreateForm


class TaskUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView,
):
    model = Task
    form_class = TaskUpdateForm

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
        task = get_object_or_404(Task, pk=self.kwargs["pk"])

        return (
            self.request.user.is_staff
            or self.request.user in task.assignees.all()
        )


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


class TaskToggleCompleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.View,
):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])

        return redirect(task.get_absolute_url())

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])

        if task.is_completed and task.deadline < datetime.date.today():
            task.deadline = datetime.date.today()

        task.is_completed = not task.is_completed
        task.save()

        referer = self.request.POST.get("referer")
        urls = {
            "home": reverse_lazy("task_manager:home"),
            "worker-detail": self.request.user.get_absolute_url() + "#tasks",
            "task-detail": task.get_absolute_url(),
            "project-detail": task.project.get_absolute_url() + "#tasks"
        }

        return redirect(
            urls.get(referer, reverse_lazy("task_manager:task-list"))
        )

    def test_func(self):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])

        return (
            self.request.user.is_staff
            or self.request.user in task.assignees.all()
            and not task.is_overdue
        )


class TaskToggleAssignView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.View,
):
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

        referer = self.request.POST.get("referer")
        urls = {
            "project-detail": task.project.get_absolute_url() + "#tasks"
        }

        return redirect(
            urls.get(referer, task.get_absolute_url())
        )

    def test_func(self):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])

        return (
            self.request.user.is_staff
            or self.request.user in task.project.members.all()
        )


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        name = self.request.GET.get("name", "")
        context["search_form"] = NameSearchForm(initial={
            "name": name,
        })
        return context

    def get_queryset(self):
        queryset = TaskType.objects.prefetch_related("tasks")

        form = NameSearchForm(self.request.GET)

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


class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        name = self.request.GET.get("name", "")
        context["search_form"] = NameSearchForm(initial={
            "name": name,
        })
        return context

    def get_queryset(self):
        queryset = Position.objects.prefetch_related("workers")

        form = NameSearchForm(self.request.GET)

        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )

        return queryset


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Position
    fields = ("name",)
    success_url = reverse_lazy("task_manager:position-list")


class PositionUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView,
):
    model = Position
    fields = ("name",)
    success_url = reverse_lazy("task_manager:position-list")

    def test_func(self):
        return self.request.user.is_staff


class PositionDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView,
):
    model = Position
    success_url = reverse_lazy("task_manager:position-list")

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
        position = self.request.GET.get("position", "")
        context["filter_form"] = WorkerFilterForm(initial={
            "position": position,
        })
        return context

    def get_queryset(self):
        queryset = Worker.objects.prefetch_related(
            "tasks"
        ).select_related("position")

        search_form = WorkerSearchForm(self.request.GET)
        filter_form = WorkerFilterForm(self.request.GET)

        if search_form.is_valid():
            queryset = queryset.filter(
                username__icontains=search_form.cleaned_data["username"]
            )

        if filter_form.is_valid():
            if not filter_form.cleaned_data["position"]:
                return queryset

            queryset = queryset.filter(
                position=filter_form.cleaned_data["position"]
            )

        return queryset


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_tasks = self.object.tasks.prefetch_related(
            "assignees",
        ).select_related("task_type", "project")

        context["completed_tasks"] = all_tasks.filter(
            is_completed=True,
        )

        context["incomplete_tasks"] = all_tasks.filter(
            is_completed=False,
        )

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


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        name = self.request.GET.get("name", "")
        context["search_form"] = NameSearchForm(initial={
            "name": name,
        })
        return context

    def get_queryset(self):
        queryset = Project.objects.prefetch_related("members", "tasks")

        form = NameSearchForm(self.request.GET)

        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )

        return queryset


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    queryset = Project.objects.prefetch_related("members__position", "tasks")

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

        context["task_create_form"] = ProjectTaskAddForm(
            initial={"project": self.object.id},
            request=self.request,
        )

        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectForm


class ProjectUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView,
):
    model = Project
    form_class = ProjectForm

    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])

        return (
            self.request.user.is_staff
            or self.request.user in project.members.all()
        )


class ProjectDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.DeleteView,
):
    model = Project
    success_url = reverse_lazy("task_manager:project-list")

    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])

        return (
            self.request.user.is_staff
            or self.request.user in project.members.all()
        )


class ProjectToggleJoinView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs["pk"])

        return redirect(project.get_absolute_url())

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs["pk"])
        user = request.user

        if user in project.members.all():
            project.members.remove(user)
            project_tasks = project.tasks.all()
            user.tasks.remove(*project_tasks)
        else:
            project.members.add(user)

        return redirect(project.get_absolute_url())
