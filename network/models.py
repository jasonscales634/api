from django.db import models

class Network(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    company = models.CharField(max_length=100)

    def __str__(self):
        return self.name
