import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Position, Project, Task, TaskType


POSITION_LIST_URL = reverse("task_manager:position-list")
PROJECT_LIST_URL = reverse("task_manager:project-list")
PROJECT_DETAIL_URL = reverse("task_manager:project-detail", kwargs={"pk": 1})
TASK_TYPE_LIST_URL = reverse("task_manager:task-type-list")
TASK_LIST_URL = reverse("task_manager:task-list")
TASK_DETAIL_URL = reverse("task_manager:task-detail", kwargs={"pk": 1})
WORKER_LIST_URL = reverse("task_manager:worker-list")
WORKER_DETAIL_URL = reverse("task_manager:worker-detail", kwargs={"pk": 1})


class PublicPositionTest(TestCase):
    def test_position_list_login_required(self):
        response = self.client.get(POSITION_LIST_URL)

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("login") + "?next=/positions/"
        )


class PrivatePositionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_positions = 12

        for position_id in range(number_of_positions):
            Position.objects.create(
                name=f"Position {position_id}",
            )

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="user12345",
            position=Position.objects.get(pk=1),
        )
        self.client.force_login(self.user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/positions/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(POSITION_LIST_URL)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(POSITION_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/position_list.html")

    def test_pagination(self):
        response = self.client.get(POSITION_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["position_list"]), 8)

    def test_lists_all_positions(self):
        response = self.client.get(POSITION_LIST_URL + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["position_list"]), 4)

    def test_search_form_exists(self):
        response = self.client.get(POSITION_LIST_URL)

        self.assertTrue("search_form" in response.context)

    def test_search_form_filters_data(self):
        response = self.client.get(POSITION_LIST_URL + "?name=Position 2")

        self.assertEqual(len(response.context["position_list"]), 1)

    def test_search_form_persists_data(self):
        response = self.client.get(POSITION_LIST_URL + "?name=Position")

        self.assertEqual(
            response.context["search_form"].initial["name"], "Position"
        )


class PublicProjectTest(TestCase):
    def test_project_list_login_required(self):
        response = self.client.get(PROJECT_LIST_URL)

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("login") + "?next=/projects/"
        )

    def test_project_detail_login_required(self):
        Project.objects.create(
            name="Test Project",
        )
        response = self.client.get(PROJECT_DETAIL_URL)

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("login") + "?next=/projects/1/"
        )


class PrivateProjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_projects = 12

        for project_id in range(number_of_projects):
            Project.objects.create(
                name=f"Project {project_id}",
            )

        Position.objects.create(
            name="Data Analyst",
        )

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="user12345",
            position=Position.objects.get(pk=1),
        )
        self.client.force_login(self.user)

    def test_list_url_exists_at_desired_location(self):
        response = self.client.get("/projects/")

        self.assertEqual(response.status_code, 200)

    def test_list_url_accessible_by_name(self):
        response = self.client.get(PROJECT_LIST_URL)

        self.assertEqual(response.status_code, 200)

    def test_list_uses_correct_template(self):
        response = self.client.get(PROJECT_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/project_list.html")

    def test_list_pagination(self):
        response = self.client.get(PROJECT_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["project_list"]), 8)

    def test_list_lists_all_projects(self):
        response = self.client.get(PROJECT_LIST_URL + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["project_list"]), 4)

    def test_create_project(self):
        user = get_user_model().objects.get(username="alice")
        form_data = {
            "name": "Website Project",
            "members": user.pk,
        }
        self.client.post(reverse("task_manager:project-create"), data=form_data)
        new_project = Project.objects.get(name=form_data["name"])

        self.assertTrue(user in new_project.members.all())

    def test_delete_project(self):
        response = self.client.get("/projects/1/delete/")

        self.assertEqual(response.status_code, 403)

        user = get_user_model().objects.get(username="alice")
        project = Project.objects.get(pk=1)
        project.members.add(user)
        project.save()

        response = self.client.get("/projects/1/delete/")

        self.assertEqual(response.status_code, 200)

    def test_detail_url_exists_at_desired_location(self):
        response = self.client.get("/projects/1/")

        self.assertEqual(response.status_code, 200)

    def test_detail_url_accessible_by_name(self):
        response = self.client.get(PROJECT_DETAIL_URL)

        self.assertEqual(response.status_code, 200)

    def test_detail_uses_correct_template(self):
        response = self.client.get(PROJECT_DETAIL_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/project_detail.html")

    def test_search_form_exists(self):
        response = self.client.get(PROJECT_LIST_URL)

        self.assertTrue("search_form" in response.context)

    def test_search_form_filters_data(self):
        response = self.client.get(PROJECT_LIST_URL + "?name=Project 5")

        self.assertEqual(len(response.context["project_list"]), 1)

    def test_search_form_persists_data(self):
        response = self.client.get(PROJECT_LIST_URL + "?name=Project")

        self.assertEqual(
            response.context["search_form"].initial["name"], "Project"
        )


class PublicTaskTypeTest(TestCase):
    def test_task_type_list_login_required(self):
        response = self.client.get(TASK_TYPE_LIST_URL)

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("login") + "?next=/task-types/"
        )


class PrivateTaskTypeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_task_types = 12

        for task_type_id in range(number_of_task_types):
            TaskType.objects.create(
                name=f"Task Type {task_type_id}",
            )

        Position.objects.create(
            name="Data Analyst",
        )

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="user12345",
            position=Position.objects.get(pk=1),
        )
        self.client.force_login(self.user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/task-types/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(TASK_TYPE_LIST_URL)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(TASK_TYPE_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/tasktype_list.html")

    def test_pagination(self):
        response = self.client.get(TASK_TYPE_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tasktype_list"]), 8)

    def test_lists_all_task_types(self):
        response = self.client.get(TASK_TYPE_LIST_URL + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tasktype_list"]), 4)

    def test_search_form_exists(self):
        response = self.client.get(TASK_TYPE_LIST_URL)

        self.assertTrue("search_form" in response.context)

    def test_search_form_filters_data(self):
        response = self.client.get(TASK_TYPE_LIST_URL + "?name=Task Type 2")

        self.assertEqual(len(response.context["tasktype_list"]), 1)

    def test_search_form_persists_data(self):
        response = self.client.get(TASK_TYPE_LIST_URL + "?name=Task Type")

        self.assertEqual(
            response.context["search_form"].initial["name"], "Task Type"
        )


class PublicTaskTest(TestCase):
    def test_task_list_login_required(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("login") + "?next=/tasks/"
        )

    def test_project_detail_login_required(self):
        project = Project.objects.create(
            name="Test Project",
        )
        task_type = TaskType.objects.create(
            name="Test Task Type"
        )

        Task.objects.create(
            name="Test Task",
            project=project,
            task_type=task_type,
            deadline=datetime.date.today(),
            priority="low",
        )
        response = self.client.get(TASK_DETAIL_URL)

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("login") + "?next=/tasks/1/"
        )


class PrivateTaskTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        project = Project.objects.create(
            name="Test Project",
        )
        task_type = TaskType.objects.create(
            name="Test Task Type"
        )
        number_of_tasks = 12

        for task_id in range(number_of_tasks):
            Task.objects.create(
                name=f"Task {task_id}",
                project=project,
                task_type=task_type,
                deadline=datetime.date.today(),
                priority="low",
            )

        Position.objects.create(
            name="Data Analyst",
        )

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="user12345",
            position=Position.objects.get(pk=1),
        )
        self.client.force_login(self.user)

    def test_list_url_exists_at_desired_location(self):
        response = self.client.get("/tasks/")

        self.assertEqual(response.status_code, 200)

    def test_list_url_accessible_by_name(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertEqual(response.status_code, 200)

    def test_list_uses_correct_template(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/task_list.html")

    def test_list_pagination(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["task_list"]), 8)

    def test_list_lists_all_tasks(self):
        response = self.client.get(TASK_LIST_URL + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["task_list"]), 4)

    def test_create_task(self):
        user = get_user_model().objects.get(username="alice")
        project = Project.objects.get(pk=1)
        project.members.add(user)
        project.save()
        task_type = TaskType.objects.get(pk=1)
        form_data = {
            "name": "Bug fix",
            "project": project.pk,
            "task_type": task_type.pk,
            "deadline": datetime.date.today(),
            "priority": "low",
        }
        self.client.post(reverse("task_manager:task-create"), data=form_data)
        new_task = Task.objects.get(name="Bug fix")

        self.assertFalse(user in new_task.assignees.all())

        new_task.assignees.add(user)
        new_task.save()
        self.assertTrue(user in new_task.assignees.all())

    def test_delete_task(self):
        response = self.client.get("/tasks/1/delete/")

        self.assertEqual(response.status_code, 403)

        user = get_user_model().objects.get(username="alice")
        task = Task.objects.get(pk=1)
        task.assignees.add(user)
        task.save()

        response = self.client.get("/tasks/1/delete/")

        self.assertEqual(response.status_code, 200)

    def test_detail_url_exists_at_desired_location(self):
        response = self.client.get("/tasks/1/")

        self.assertEqual(response.status_code, 200)

    def test_detail_url_accessible_by_name(self):
        response = self.client.get(TASK_DETAIL_URL)

        self.assertEqual(response.status_code, 200)

    def test_detail_uses_correct_template(self):
        response = self.client.get(TASK_DETAIL_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/task_detail.html")

    def test_search_form_exists(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertTrue("search_form" in response.context)

    def test_search_form_filters_data(self):
        response = self.client.get(TASK_LIST_URL + "?name=Task 5")

        self.assertEqual(len(response.context["task_list"]), 1)

    def test_search_form_persists_data(self):
        response = self.client.get(TASK_LIST_URL + "?name=Task")

        self.assertEqual(
            response.context["search_form"].initial["name"], "Task"
        )

    def test_filter_form_exists(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertTrue("filter_form" in response.context)

    def test_filter_form_filters_data(self):
        response = self.client.get(
            TASK_LIST_URL + "?project=1&task_type=1"
        )

        self.assertEqual(len(response.context["task_list"]), 8)

    def test_filter_form_persists_data(self):
        response = self.client.get(
            TASK_LIST_URL + "?project=1&task_type=1"
        )

        self.assertEqual(
            response.context["filter_form"].initial["project"], "1"
        )
        self.assertEqual(
            response.context["filter_form"].initial["task_type"], "1"
        )

class PublicWorkerTest(TestCase):
    def test_worker_list_login_required(self):
        response = self.client.get(WORKER_LIST_URL)

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("login") + "?next=/team/"
        )

    def test_worker_detail_login_required(self):
        position = Position.objects.create(
            name="Data Analyst",
        )

        get_user_model().objects.create_user(
            username="bob",
            password="user12345",
            position=position,
        )
        response = self.client.get(WORKER_DETAIL_URL)

        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse("login") + "?next=/team/1/"
        )

    def test_sign_up(self):
        position = Position.objects.create(
            name="Data Analyst",
        )
        form_data = {
            "username": "charlie",
            "position": position.pk,
            "password1": "fj2489eq7",
            "password2": "fj2489eq7",
            "first_name": "Charlie",
            "last_name": "Smith",
        }
        self.client.post(reverse("task_manager:sign-up"), data=form_data)
        new_user = get_user_model().objects.get(
            username=form_data["username"]
        )

        self.assertEqual(new_user.first_name, form_data["first_name"])
        self.assertEqual(new_user.last_name, form_data["last_name"])
        self.assertEqual(new_user.position, position)


class PrivateWorkerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_workers = 10

        position = Position.objects.create(
            name="Data Analyst"
        )

        for worker_id in range(number_of_workers):
            get_user_model().objects.create_user(
                username=f"User {worker_id}",
                password="user12345",
                position=position,
            )

    def setUp(self):
        position = Position.objects.create(
            name="Systems Analyst"
        )

        self.user = get_user_model().objects.create_user(
            username="alice",
            password="user12321",
            position=position,
        )
        self.client.force_login(self.user)

    def test_list_url_exists_at_desired_location(self):
        response = self.client.get("/team/")

        self.assertEqual(response.status_code, 200)

    def test_list_url_accessible_by_name(self):
        response = self.client.get(WORKER_LIST_URL)

        self.assertEqual(response.status_code, 200)

    def test_list_uses_correct_template(self):
        response = self.client.get(WORKER_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/worker_list.html")

    def test_list_pagination(self):
        response = self.client.get(WORKER_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["worker_list"]), 8)

    def test_list_lists_all_workers(self):
        response = self.client.get(WORKER_LIST_URL + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["worker_list"]), 3)

    def test_delete_worker(self):
        response = self.client.get("/team/1/delete/")

        self.assertEqual(response.status_code, 403)

    def test_detail_url_exists_at_desired_location(self):
        response = self.client.get("/team/1/")

        self.assertEqual(response.status_code, 200)

    def test_detail_url_accessible_by_name(self):
        response = self.client.get(WORKER_DETAIL_URL)

        self.assertEqual(response.status_code, 200)

    def test_detail_uses_correct_template(self):
        response = self.client.get(WORKER_DETAIL_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/worker_detail.html")

    def test_search_form_exists(self):
        response = self.client.get(WORKER_LIST_URL)

        self.assertTrue("search_form" in response.context)

    def test_search_form_filters_data(self):
        response = self.client.get(WORKER_LIST_URL + "?username=alice")

        self.assertEqual(len(response.context["worker_list"]), 1)

    def test_search_form_persists_data(self):
        """Tests that search form initial data is persisted"""
        response = self.client.get(WORKER_LIST_URL + "?username=alice")

        self.assertEqual(
            response.context["search_form"].initial["username"], "alice"
        )

    def test_filter_form_exists(self):
        response = self.client.get(WORKER_LIST_URL)

        self.assertTrue("filter_form" in response.context)

    def test_filter_form_filters_data(self):
        response = self.client.get(
            WORKER_LIST_URL + "?position=2"
        )

        self.assertEqual(len(response.context["worker_list"]), 1)

    def test_filter_form_persists_data(self):
        response = self.client.get(
            WORKER_LIST_URL + "?position=2"
        )

        self.assertEqual(
            response.context["filter_form"].initial["position"], "2"
        )
