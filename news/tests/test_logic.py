from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING
from http import HTTPStatus

User = get_user_model()

class TestCommentCreation(TestCase):
    COMMENT_TEXT = 'Comment text'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='News', text='text') # type: ignore
        cls.url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'text': cls.COMMENT_TEXT,
        }

    def test_anonymous_user_cant_create_comment(self):
        response = self.client.post(self.url, data=self.form_data)
        count = Comment.objects.count() # type: ignore
        self.assertEqual(count, 0)

    def test_user_can_create_comment(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{self.url}#comments')
        comments_count = Comment.objects.count() # type: ignore
        self.assertEqual(comments_count, 1)
        comment = Comment.objects.get() # type: ignore
        self.assertEqual(comment.text, self.COMMENT_TEXT)
        self.assertEqual(comment.news, self.news)
        self.assertEqual(comment.author, self.author)

    def test_user_cant_use_bad_words(self):
        # Формируем данные для отправки формы; текст включает
        # первое слово из списка стоп-слов.
        bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
        # Отправляем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=bad_words_data)
        # Проверяем, есть ли в ответе ошибка формы.
        self.assertFormError(response, 'form', 'text', WARNING)
        # Дополнительно убедимся, что комментарий не был создан.
        comments_count = Comment.objects.count() # type: ignore
        self.assertEqual(comments_count, 0) 

class TestCommentEditDelete(TestCase):
    COMMENT_TEXT = 'Comment text'
    UPDATED_COMMENT_TEXT = 'Updated comment text'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='News', text='text') # type: ignore
        news_url = reverse('news:detail', args=(cls.news.id,))
        cls.url_to_comment = news_url + '#comments'
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.comment = Comment.objects.create( # type: ignore
            news=cls.news,
            author=cls.author,
            text=cls.COMMENT_TEXT,
        )
        cls.url_to_edit = reverse('news:edit', args=(cls.comment.id,))
        cls.url_to_delete = reverse('news:delete', args=(cls.comment.id,))
        cls.form_data = {
            'text': cls.UPDATED_COMMENT_TEXT,
        }

    def test_author_can_delete_comment(self):
        response = self.author_client.post(self.url_to_delete)
        self.assertRedirects(response, self.url_to_comment)
        self.assertEqual(response.status_code, HTTPStatus.FOUND) # type: ignore
        comments_count = Comment.objects.count() # type: ignore
        self.assertEqual(comments_count, 0)

    def test_user_cant_delete_comment_of_another_user(self):
        response = self.reader_client.post(self.url_to_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND) # type: ignore
        comments_count = Comment.objects.count() # type: ignore
        self.assertEqual(comments_count, 1)

    def test_author_can_edit_comment(self):
        response = self.author_client.post(self.url_to_edit, data=self.form_data)
        self.assertRedirects(response, self.url_to_comment)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, self.UPDATED_COMMENT_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.url_to_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND) # type: ignore
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, self.COMMENT_TEXT)

