# news/tests/test_trial.py
from unittest import skip
from django.test import TestCase

from news.models import News


class TestNews(TestCase):
    # Все нужные переменные сохраняем в атрибуты класса.
    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'
    
    
    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create( # type: ignore
            # При создании объекта обращаемся к константам класса через cls.
            title=cls.TITLE,
            text=cls.TEXT,
        )

    @skip('Пропускаем тест на время')
    def test_successful_creation(self):
        news_count = News.objects.count() # type: ignore
        self.assertEqual(news_count, 1)

    @skip('Пропускаем тест на время')
    def test_title(self):
        # Чтобы проверить равенство с константой -
        # обращаемся к ней через self, а не через cls:
        self.assertEqual(self.news.title, self.TITLE)