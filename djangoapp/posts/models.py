from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class PostModel(models.Model):
    poster_user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_content = models.CharField(max_length=280)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    likes_counter = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.poster_user.username}: {self.text_content[:20]}..."