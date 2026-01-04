from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField()
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} by {self.author}'
    

class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f'{self.follower} follows {self.following}'
    

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    liked_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f'{self.liked_by.username} liked podt with id {self.liked_post.id}'

