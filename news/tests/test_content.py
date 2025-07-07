from turtle import title
from django.test import TestCase
from django.urls import reverse
from news.models import News, Comment
from yanews import settings
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from news.forms import CommentForm

User = get_user_model()

class TestHomePage(TestCase):

    HOME_PAGE_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        news_list = [
            News(
                title=f'News {index}',
                text=f'text {index}',
                date=datetime.today() - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(news_list) # type: ignore

    def test_news_count_on_home_page(self):
        response = self.client.get(self.HOME_PAGE_URL)
        object_list = response.context['object_list'] # type: ignore
        news_count = len(object_list)
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        response = self.client.get(self.HOME_PAGE_URL)
        object_list = response.context['object_list'] # type: ignore
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='News', text='text') # type: ignore
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='author')
        now = timezone.now()
        for index in range(10):
            comment = Comment.objects.create( # type: ignore
                news=cls.news,
                author=cls.author,
                text = f'Comment {index}')
            comment.created = now + timedelta(days=index)
            comment.save()

    def test_comments_order(self):
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context) # type: ignore
        news = response.context['news'] # type: ignore
        all_comments = news.comment_set.all()
        all_times = [comment.created for comment in all_comments]
        sorted_times = sorted(all_times)
        self.assertEqual(all_times, sorted_times)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context) # type: ignore
        
    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context) # type: ignore
        self.assertIsInstance(response.context['form'], CommentForm) # type: ignore
