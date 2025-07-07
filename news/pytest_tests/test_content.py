from django.urls import reverse
from yanews import settings
import pytest
from pytest_lazy_fixtures import lf    

def test_news_count_on_home_page(author_client, news_list):
    home_url = reverse('news:home') 
    response = author_client.get(home_url)
    object_list = response.context['object_list'] # type: ignore
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

def test_news_order(author_client, news_list):
    home_url = reverse('news:home')
    response = author_client.get(home_url)
    object_list = response.context['object_list'] # type: ignore
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates    

def test_comments_order(author_client, comment_list):
    detail_url = reverse('news:detail', args=[comment_list[0].news.id]) # type: ignore
    response = author_client.get(detail_url)
    news = response.context['news'] # type: ignore
    all_comments = news.comment_set.all()
    all_times = [comment.created for comment in all_comments]
    sorted_times = sorted(all_times)
    assert all_times == sorted_times

@pytest.mark.parametrize(
    'parametrized_client, note_should_be_in_list',
    (
        (lf('author_client'), True),
        (lf('client'), False),
    )
)
def test_form_availability_for_different_users(
    news,
    parametrized_client,
    note_should_be_in_list,
):
    detail_url = reverse('news:detail', args=[news.id])
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) == note_should_be_in_list