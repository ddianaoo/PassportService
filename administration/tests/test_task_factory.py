from django.test import TestCase
from administration.factories import TaskFactory


class TestFactories(TestCase):
    def test_passport_factory(self):
        task = TaskFactory()
        self.assertIsNotNone(task.user)
        self.assertIsNotNone(task.title)
        self.assertIsNotNone(task.status)
        self.assertIsNotNone(task.status)
        self.assertIsNotNone(task.created_at)
