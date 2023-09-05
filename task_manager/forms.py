import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Worker, Task


class SignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "position",
            "first_name",
            "last_name",
            "email",
        )


class TaskForm(forms.ModelForm):

    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    deadline = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date"}
        )
    )

    class Meta:
        model = Task
        fields = (
            "name",
            "description",
            "deadline",
            "priority",
            "task_type",
            "assignees",
        )

    def clean_deadline(self):
        return validate_deadline(self.cleaned_data["deadline"])


class TaskRenewForm(forms.ModelForm):

    deadline = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date"}
        )
    )

    class Meta:
        model = Task
        fields = ("deadline",)

    def clean_deadline(self):
        return validate_deadline(self.cleaned_data["deadline"])


def validate_deadline(deadline):
    if deadline <= datetime.date.today():
        raise ValidationError("Invalid date - deadline set in past")

    return deadline


class WorkerUpdateForm(forms.ModelForm):

    class Meta:
        model = Worker
        fields = (
            "first_name",
            "last_name",
            "position",
        )


class CustomSearch(Field):
    template = "fields/custom_search.html"


class NameSearchHelper(FormHelper):

    form_method = "GET"
    layout = Layout(
        CustomSearch("name"),
    )


class TaskSearchForm(forms.Form):

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
        self.helper = NameSearchHelper()


class TaskTypeSearchForm(forms.Form):

    name = forms.CharField(
        max_length=32,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by name"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = NameSearchHelper()


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
