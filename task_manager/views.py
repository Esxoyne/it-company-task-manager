from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import SignUpForm
from .models import Worker, Task


class Index(generic.ListView):
    model = Worker
    template_name = "task_manager/index.html"


def toggle_theme(request, **kwargs):
    if "is_dark_mode" in request.session:
        is_dark_mode = request.session.get("is_dark_mode")
        request.session["is_dark_mode"] = not is_dark_mode
    else:
        request.session["is_dark_mode"] = True
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class TaskListView(generic.ListView):
    model = Task


class WorkerListView(generic.ListView):
    model = Worker


class SignUpView(generic.CreateView):
    model = Worker
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")
