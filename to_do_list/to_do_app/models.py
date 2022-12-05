from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Task(models.Model):
    task_title = models.CharField(max_length=60)
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # If a author is deleted, then all his tasks will also be deleted since CASCADE option is set
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.task_title

    class Meta:
        ordering = ('-updated_at',)
        db_table = 'tbl_task'