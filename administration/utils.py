from .models import Task

TITLE_NAMES = [title[0] for title in Task.TITLE_CHOICES]
TITLE_SLUGS = ['-'.join(title.split()) for title in TITLE_NAMES]
TITLE_NAMES_AND_SLUGS = [[a, b] for a, b in zip(TITLE_SLUGS, TITLE_NAMES)]
DICT_TITLES_SLUGS = dict(zip(TITLE_NAMES, TITLE_SLUGS))
