from django.utils import timezone
import factory
import factory.fuzzy

from authentication.factories import CustomUserFactory
from .models import Task
from . import signals


@factory.django.mute_signals(signals.post_save)
class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    user       = factory.SubFactory(CustomUserFactory)
    title      = factory.fuzzy.FuzzyChoice(Task.TITLE_CHOICES, getter=lambda c: c[0])
    status     = factory.fuzzy.FuzzyChoice(Task.STATUS_CHOICES, getter=lambda c: c[0])
    user_data  = factory.LazyAttribute(lambda _: dict())
    created_at = factory.LazyFunction(timezone.now)
