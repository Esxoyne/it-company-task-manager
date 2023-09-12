import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase

from task_manager.models import Position, Project, Task, TaskType, Worker


class PositionModelTest(TestCase):
    def test_position_str(self):
        position = Position.objects.create(
            name="Data Analyst",
        )

        self.assertEqual(str(position), position.name)


class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        project = Project.objects.create(
            name="Task Manager",
        )

        task_type = TaskType.objects.create(
            name="New feature",
        )

        number_of_tasks = 10
        for _ in range(number_of_tasks):
            Task.objects.create(
                name="Task",
                project=project,
                task_type=task_type,
                deadline=(
                    datetime.date.today()
                    + datetime.timedelta(days=1)
                ),
                priority="low",
            )

        Task.objects.filter(id__range=(1, 4)).update(is_completed=True)


    def test_project_str(self):
        project = Project.objects.get(pk=1)

        self.assertEqual(str(project), project.name)

    def test_project_get_absolute_url(self):
        project = Project.objects.get(pk=1)
        expected = "/projects/1/"

        self.assertEqual(project.get_absolute_url(), expected)

    def test_project_progress(self):
        project = Project.objects.get(pk=1)

        self.assertEqual(project.progress, 0.4)
        self.assertEqual(project.get_progress(), "40")


class TaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        project = Project.objects.create(
            name="Task Manager",
        )

        task_type = TaskType.objects.create(
            name="New feature",
        )

        task = Task.objects.create(
            name="Task",
            project=project,
            task_type=task_type,
            deadline=(
                datetime.date.today()
                + datetime.timedelta(days=2)
            ),
            priority="low",
        )

        task.pk = None
        task.deadline=(
            datetime.date.today()
            + datetime.timedelta(days=1)
        )
        task.save()

        task.pk = None
        task.deadline=(
            datetime.date.today()
            - datetime.timedelta(days=1)
        )
        task.save()

    def test_task_str(self):
        task = Task.objects.get(pk=1)

        self.assertEqual(str(task), "Task")

    def test_task_get_absolute_url(self):
        task = Task.objects.get(pk=1)
        expected = "/tasks/1/"

        self.assertEqual(task.get_absolute_url(), expected)

    def test_task_is_at_risk(self):
        task_1 = Task.objects.get(pk=1)
        task_2 = Task.objects.get(pk=2)
        task_3 = Task.objects.get(pk=3)

        self.assertEqual(task_1.is_at_risk, False)
        self.assertEqual(task_2.is_at_risk, True)
        self.assertEqual(task_3.is_at_risk, False)

    def test_task_is_overdue(self):
        task_1 = Task.objects.get(pk=1)
        task_2 = Task.objects.get(pk=2)
        task_3 = Task.objects.get(pk=3)

        self.assertEqual(task_1.is_overdue, False)
        self.assertEqual(task_2.is_overdue, False)
        self.assertEqual(task_3.is_overdue, True)


class TaskTypeModelTest(TestCase):
    def test_position_str(self):
        task_type = TaskType.objects.create(
            name="New feature",
        )

        self.assertEqual(str(task_type), task_type.name)


class WorkerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        position = Position.objects.create(
            name="Data Analyst"
        )

        get_user_model().objects.create_user(
            username="alice",
            password="user12345",
            first_name="Alice",
            last_name="Smith",
            position=position
        )

    def test_worker_str(self):
        worker = Worker.objects.get(pk=1)
        expected = "alice (Alice Smith)"

        self.assertEqual(str(worker), expected)

    def test_worker_get_absolute_url(self):
        worker = Worker.objects.get(pk=1)
        expected = "/team/1/"

        self.assertEqual(worker.get_absolute_url(), expected)
