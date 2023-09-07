import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class Project(models.Model):
    name = models.CharField(max_length=64, unique=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
    )
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("task_manager:project-detail", kwargs={"pk": self.pk})

    @property
    def progress(self) -> float:
        total = self.tasks.count()
        if not total:
            return "0"

        completed = self.tasks.filter(is_completed=True).count()
        return completed / total

    def get_progress(self) -> str:
        return str(int(self.progress * 100))


class Position(models.Model):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name="workers",
        null=True,
    )

    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.username} ({self.first_name} {self.last_name})"

    def get_absolute_url(self) -> str:
        return reverse("task_manager:worker-detail", kwargs={"pk": self.pk})


class TaskType(models.Model):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=16,
        choices=Priority.choices,
        default=Priority.LOW,
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tasks",
    )

    class Meta:
        ordering = ["deadline"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("task_manager:task-detail", kwargs={"pk": self.pk})

    @property
    def is_at_risk(self) -> bool:
        return (
            datetime.date.today()
            < self.deadline
            <= datetime.date.today() + datetime.timedelta(days=2)
        )

    @property
    def is_overdue(self) -> bool:
        return self.deadline <= datetime.date.today() and not self.is_completed
