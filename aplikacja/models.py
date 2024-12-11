from django.db import models

class ScheduleEvent(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planowe'),
        ('canceled', 'Odwołane'),
        ('extra', 'Dodatkowe'),
    ]

    title = models.CharField(max_length=200, default="Podlewanie")
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='planned',
    )

    def __str__(self):
        return f"{self.title} ({self.start} - {self.end})"