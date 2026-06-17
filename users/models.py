from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)

    
    def __str__(self):
        console.log(username)
        return self.username
