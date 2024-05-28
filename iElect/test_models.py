from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Election, Candidate, ControlVote

class ElectionModelTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.create(
            title='Test Election',
            description='Test Election Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

    def test_election_creation(self):
        self.assertEqual(self.election.title, 'Test Election')
        self.assertEqual(self.election.description, 'Test Election Description')
        self.assertTrue(self.election.start_date <= timezone.now())
        self.assertTrue(self.election.end_date >= timezone.now())

class CandidateModelTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.create(
            title='Test Election',
            description='Test Election Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )
        self.candidate = Candidate.objects.create(
            election=self.election,
            name='Test Candidate',
            position='Test Position',
            bio='Test Bio'
        )

    def test_candidate_creation(self):
        self.assertEqual(self.candidate.name, 'Test Candidate')
        self.assertEqual(self.candidate.position, 'Test Position')

    def test_get_vote_count(self):
        # Create some control votes for the candidate
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        ControlVote.objects.create(user=user1, position=self.candidate, status=True)
        ControlVote.objects.create(user=user2, position=self.candidate, status=True)
        
        self.assertEqual(self.candidate.get_vote_count(), 2)

    def test_user_has_voted(self):
        user = User.objects.create(username='testuser')
        control_vote = ControlVote.objects.create(user=user, position=self.candidate, status=True)
        self.assertTrue(control_vote.user_has_voted(user, self.candidate))

    def test_update_vote_count(self):
        # Create some control votes for the candidate
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        ControlVote.objects.create(user=user1, position=self.candidate, status=True)
        ControlVote.objects.create(user=user2, position=self.candidate, status=True)
        
        self.candidate.update_vote_count()
        self.assertEqual(self.candidate.total_vote, 2)

class ControlVoteModelTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.create(
            title='Test Election',
            description='Test Election Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )
        self.candidate = Candidate.objects.create(
            election=self.election,
            name='Test Candidate',
            position='Test Position',
            bio='Test Bio'
        )
        self.user = User.objects.create(username='testuser')

    def test_control_vote_creation(self):
        control_vote = ControlVote.objects.create(user=self.user, position=self.candidate, status=True)
        self.assertEqual(control_vote.user.username, 'testuser')
        self.assertEqual(control_vote.position.name, 'Test Candidate')
        self.assertTrue(control_vote.status)

    def test_user_has_voted(self):
        control_vote = ControlVote.objects.create(user=self.user, position=self.candidate, status=True)
        self.assertTrue(control_vote.user_has_voted(self.user, self.candidate))

    def test_save_method_updates_vote_count(self):
        initial_vote_count = self.candidate.get_vote_count()
        control_vote = ControlVote.objects.create(user=self.user, position=self.candidate, status=True)
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.get_vote_count(), initial_vote_count + 1)
