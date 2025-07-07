from news.models import Comment
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from http import HTTPStatus


def test_anonymous_user_cant_create_comment(client, form_data, news_id):
    url = reverse('news:detail', args=(news_id,))
    response = client.post(url, data=form_data)
    count = Comment.objects.count()
    assert count == 0

def test_user_can_create_comment(author_client, form_data, news_id):
    url = reverse('news:detail', args=(news_id,))
    response = author_client.post(url, data=form_data)
    count = Comment.objects.count()
    assert count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']

def test_user_cant_use_bad_words(author_client, form_data, news_id):
    url = reverse('news:detail', args=(news_id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assert 'form' in response.context
    form = response.context['form']
    assert form.errors
    assert 'text' in form.errors
    assert WARNING in str(form.errors['text'])
    count = Comment.objects.count()
    assert count == 0

def test_author_can_delete_comment(author_client, form_data, news_id, comment_id):
    count = Comment.objects.count()
    assert count == 1
    url = reverse('news:delete', args=(comment_id,))
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    count = Comment.objects.count()
    assert count == 0

def test_user_cant_delete_comment_of_another_user(reader_client, form_data, news_id, comment_id):
    url = reverse('news:delete', args=(comment_id,))
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    count = Comment.objects.count()
    assert count == 1

def test_author_can_edit_comment(author_client, form_data, news_id, comment, comment_id):
    url = reverse('news:edit', args=(comment_id,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']

def test_user_cant_edit_comment_of_another_user(reader_client, form_data, comment, comment_id):
    url = reverse('news:edit', args=(comment_id,))
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment.text
