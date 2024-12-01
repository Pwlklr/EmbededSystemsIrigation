from django.db import models

class ScheduleEvent(models.Model):
    title = models.CharField(max_length=200, default="Podlewanie")
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return f"{self.title} ({self.start} - {self.end})"