from django.contrib import admin
from .models import Election,ControlVote,Candidate, UserVote

admin.site.register(Election)
admin.site.register(Candidate)
admin.site.register(ControlVote)
admin.site.register(UserVote)
