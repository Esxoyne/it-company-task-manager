import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase

from task_manager.forms import (
    CustomSearch,
    NameSearchForm,
    ProjectTaskAddForm,
    TaskCreateForm,
    TaskFilterForm,
    TaskUpdateForm,
    TaskRenewForm,
    ProjectForm,
    WorkerFilterForm,
    WorkerSearchForm,
)
from task_manager.models import Position, Project, Task, TaskType


class TaskCreateFormTest(TestCase):
    def test_task_create_form_deadline_field_widget(self):
        form = TaskCreateForm()

        self.assertTrue(isinstance(form.fields["deadline"].widget, forms.DateInput))

    def test_task_create_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = TaskCreateForm(data={"deadline": date})
        self.assertFalse(form.is_valid())


class TaskUpdateFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        position = Position.objects.create(
            name="Data Analyst"
        )

        user_1 = get_user_model().objects.create_user(
            username="alice",
            password="user12345",
            position=position
        )

        get_user_model().objects.create_user(
            username="bob",
            password="user12345",
            position=position
        )

        project = Project.objects.create(
            name="Task Manager",
        )
        project.members.set((user_1,))

        task_type = TaskType.objects.create(
            name="New feature",
        )

        Task.objects.create(
            name="Task",
            project=project,
            task_type=task_type,
            deadline=(
                datetime.date.today()
                + datetime.timedelta(days=2)
            ),
            priority="low",
        )

    def test_task_update_form_assignees_field_widget(self):
        task = Task.objects.get(pk=1)
        form = TaskUpdateForm(instance=task)

        self.assertTrue(isinstance(form.fields["assignees"].widget, forms.CheckboxSelectMultiple))

    def test_task_update_form_assignees_field_queryset(self):
        task = Task.objects.get(pk=1)
        form = TaskUpdateForm(instance=task)
        project_members = Project.objects.get(pk=1).members.all()

        self.assertEqual(
            len(form.fields["assignees"].queryset), 1
        )

    def test_task_update_form_deadline_field_widget(self):
        task = Task.objects.get(pk=1)
        form = TaskUpdateForm(instance=task)

        self.assertTrue(isinstance(form.fields["deadline"].widget, forms.DateInput))

    def test_task_update_form_date_in_past(self):
        task = Task.objects.get(pk=1)
        data = {
            "name": task.name,
            "project": task.project,
            "task_type": task.task_type,
            "deadline": (
                datetime.date.today()
                - datetime.timedelta(days=1)
            ),
            "priority": task.priority,
        }
        form = TaskUpdateForm(data, instance=task)
        self.assertFalse(form.is_valid())

    def test_task_update_form_date_today(self):
        task = Task.objects.get(pk=1)
        data = {
            "name": task.name,
            "project": task.project,
            "task_type": task.task_type,
            "deadline": (
                datetime.date.today()
            ),
            "priority": task.priority,
        }
        form = TaskUpdateForm(data, instance=task)
        self.assertTrue(form.is_valid())


class TaskRenewFormTest(TestCase):
    def test_task_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = TaskRenewForm(data={"deadline": date})
        self.assertFalse(form.is_valid())

    def test_task_renew_form_date_today(self):
        date = datetime.date.today()
        form = TaskRenewForm(data={"deadline": date})
        self.assertTrue(form.is_valid())


class ProjectFormTest(TestCase):
    def test_project_form_members_field_widget(self):
        form = ProjectForm()

        self.assertTrue(
            isinstance(
                form.fields["members"].widget, forms.CheckboxSelectMultiple
            )
        )


class ProjectTaskAddFormTest(TestCase):
    def test_project_task_add_form_project_field_widget(self):
        form = ProjectTaskAddForm()

        self.assertTrue(
            isinstance(
                form.fields["project"].widget, forms.HiddenInput
            )
        )


class SearchFormTest(TestCase):
    def setUp(self):
        self.name_form = NameSearchForm()
        self.username_form = WorkerSearchForm()

    def test_search_form_name_field_widget(self):
        self.assertTrue(
            isinstance(
                self.name_form.fields["name"].widget, forms.TextInput
            )
        )
        self.assertTrue(
            isinstance(
                self.username_form.fields["username"].widget, forms.TextInput
            )
        )

    def test_search_form_labels(self):
        self.assertEqual(self.name_form.fields["name"].label, "")
        self.assertEqual(self.username_form.fields["username"].label, "")

    def test_search_form_helpers(self):
        self.assertTrue(isinstance(self.name_form.helper, FormHelper))
        self.assertEqual(self.name_form.helper.form_method, "get")

        self.assertTrue(isinstance(self.username_form.helper, FormHelper))
        self.assertEqual(self.username_form.helper.form_method, "get")


class FilterFormTest(TestCase):
    def test_filter_form_labels(self):
        self.assertEqual(TaskFilterForm().fields["project"].label, "Project")
        self.assertEqual(
            WorkerFilterForm().fields["position"].label, "Position"
        )
