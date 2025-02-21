from django.db import models

class Submission(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.rut}"
