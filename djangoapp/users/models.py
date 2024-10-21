from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers_profiles", blank=True
    )

    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following_profiles", blank=True
    )

    def __str__(self):
        return self.user.username
