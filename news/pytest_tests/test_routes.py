from news.models import News
import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_lazy_fixtures import lf


@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', lf('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ]
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    if args is not None:
        url = reverse(name, args=(args,))
    else:
        url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK



@pytest.mark.parametrize(
 'parametrized_client, expected_status',
 [
    (lf('author_client'), HTTPStatus.OK),
    (lf('reader_client'), HTTPStatus.NOT_FOUND),
 ]
)
@pytest.mark.parametrize(
    "name",
    [
        "news:edit",
        "news:delete",
    ]
)   
def test_availability_for_comment_edit_and_delete(parametrized_client, expected_status, name, comment):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    [
        'news:edit',
        'news:delete',
    ]
)
def test_redirect_for_anonymous_client(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
