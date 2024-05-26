from django.test import TestCase
from .models import Election, Candidate, ControlVote, UserVote
from django.contrib.auth.models import User

class ElectionTest(TestCase):
  def setUp(self):
      self.election = Election.objects.create(title='Test Election', description='Test Description', start_date='2022-01-01T00:00:00Z', end_date='2022-01-02T00:00:00Z')

  def test_election_creation(self):
      self.assertEqual(self.election.title, 'Test Election')

class CandidateTest(TestCase):
   def setUp(self):
       election = Election.objects.create(title='Test Election', description='Test Description', start_date='2022-01-01T00:00:00Z', end_date='2022-01-02T00:00:00Z')
       Candidate.objects.create(election=election, name='Test Candidate', position='Test Position', bio='Test Bio')

   def test_candidate_creation(self):
       candidate = Candidate.objects.get(id=1)
       self.assertEqual(candidate.name, 'Test Candidate')

class ControlVoteTest(TestCase):
   def setUp(self):
       user = User.objects.create_user('testuser', 'test@example.com', 'password')
       election = Election.objects.create(title='Test Election', description='Test Description', start_date='2022-01-01T00:00:00Z', end_date='2022-01-02T00:00:00Z')
       candidate = Candidate.objects.create(election=election, name='Test Candidate', position='Test Position', bio='Test Bio')
       ControlVote.objects.create(user=user, position=candidate, status=False)

   def test_controlvote_creation(self):
       controlvote = ControlVote.objects.get(id=1)
       self.assertEqual(controlvote.status, False)

class UserVoteTest(TestCase):
   def setUp(self):
       user = User.objects.create_user('testuser', 'test@example.com', 'password')
       election = Election.objects.create(title='Test Election', description='Test Description', start_date='2022-01-01T00:00:00Z', end_date='2022-01-02T00:00:00Z')
       UserVote.objects.create(user=user, election=election)

   def test_uservote_creation(self):
       uservote = UserVote.objects.get(id=1)
       self.assertEqual(uservote.user.username, 'testuser')