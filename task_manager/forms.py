import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Position, TaskType, Worker, Task, Project


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "position",
            "first_name",
            "last_name",
            "email",
        )


class TaskCreateForm(forms.ModelForm):
    deadline = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "onfocus": "this.showPicker()",
            }
        )
    )

    class Meta:
        model = Task
        fields = (
            "name",
            "description",
            "project",
            "task_type",
            "priority",
            "deadline",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5})
        }

    def clean_deadline(self):
        return validate_deadline(self.cleaned_data["deadline"])

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if self.request:
            self.fields["project"].queryset = self.request.user.projects.all()


class TaskUpdateForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    deadline = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "onfocus": "this.showPicker()",
            }
        )
    )

    class Meta:
        model = Task
        fields = (
            "name",
            "description",
            "task_type",
            "priority",
            "deadline",
            "assignees",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5})
        }

    def clean_deadline(self):
        return validate_deadline(self.cleaned_data["deadline"])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignees"].queryset = self.instance.project.members.all()


class TaskRenewForm(forms.ModelForm):
    deadline = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "onfocus": "this.showPicker()",
            }
        )
    )

    class Meta:
        model = Task
        fields = ("deadline",)

    def clean_deadline(self):
        return validate_deadline(self.cleaned_data["deadline"])


def validate_deadline(deadline):
    if deadline < datetime.date.today():
        raise ValidationError("Invalid date - deadline set in past")

    return deadline


class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Project
        fields = (
            "name",
            "description",
            "members",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5})
        }


class ProjectTaskAddForm(TaskCreateForm):
    project = forms.IntegerField(widget=forms.HiddenInput())


class WorkerUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = (
            "first_name",
            "last_name",
            "email",
            "position",
        )


class CustomSearch(Field):
    template = "fields/custom_search.html"


class NameSearchForm(forms.Form):
    name = forms.CharField(
        max_length=64,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by name"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            CustomSearch("name"),
        )


class WorkerSearchForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by username"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            CustomSearch("username"),
        )


class TaskFilterForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        label="Project",
    )
    task_type = forms.ModelChoiceField(
        queryset=TaskType.objects.all(),
        required=False,
        label="Type"
    )


class WorkerFilterForm(forms.Form):
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        required=False,
        label="Position",
    )
