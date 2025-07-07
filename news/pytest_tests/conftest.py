import pytest
from django.test.client import Client
from news.models import News, Comment
from datetime import datetime, timedelta
from yanews import settings
from django.utils import timezone

@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')

@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='reader')

@pytest.fixture
def news(author):
    return News.objects.create( # type: ignore
        title='Test news',
        text='Test text',
    )

@pytest.fixture
def news_list(author):
    news_list = [
        News(
            title=f'News {index}',
            text=f'text {index}',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(news_list) # type: ignore

@pytest.fixture
def comment(news, author):
    return Comment.objects.create( # type: ignore
        news=news,
        author=author,
        text='Test comment',
    )

@pytest.fixture
def news_id(news):
    return news.pk

@pytest.fixture
def comment_id(comment):
    return comment.pk

@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client

@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client

@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create( # type: ignore
            news=news,
            author=author,
            text = f'Comment {index}')
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments

@pytest.fixture
def form_data():
    return {
        'text': 'Updated comment text',
    }