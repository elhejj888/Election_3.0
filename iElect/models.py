from django.db import models
from django.contrib.auth.models import User

class Election(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.title

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='candidate_pictures/', null=True, blank=True)
    bio = models.TextField()
    total_vote = models.IntegerField(default=0, editable=False)
    def __str__(self):
        return self.name

class ControlVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=255)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.position} - {'Voted' if self.status else 'Not Voted'}"



