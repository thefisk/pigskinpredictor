from django.db import models
from django.utils import timezone
from accounts.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    short_content = models.TextField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.short_content = self.content[0:120]+"..."
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.id)])

    class Meta:
        verbose_name_plural = "Updates"
        ordering = ['-date_posted',]