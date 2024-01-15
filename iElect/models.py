from django.db import IntegrityError, models
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

   def user_has_voted(self, user):
       control_vote = ControlVote.objects.filter(user=user, position=self).first()
       return control_vote.user_has_voted(user, self) if control_vote else False
    
   def update_vote_count(self):
        self.total_vote = self.controlvote_set.count()
        self.save()

   def __str__(self):
       return self.name
class ControlVote(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   position = models.ForeignKey(Candidate, on_delete=models.CASCADE)
   status = models.BooleanField(default=False)

   def __str__(self):
       return f"{self.user.username} - {self.position.name} - {'Voted' if self.status else 'Not Voted'}"

   def user_has_voted(self, user, candidate):
       return ControlVote.objects.filter(user=user, position=candidate).exists()

   def save(self, *args, **kwargs):
       super().save(*args, **kwargs)
       self.position.update_vote_count()
  
class UserVote(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   election = models.ForeignKey(Election, on_delete=models.CASCADE)