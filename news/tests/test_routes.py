# news/tests/test_routes.py
from django.test import TestCase
from unittest import skip
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from news.models import News, Comment

User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create( # type: ignore
            title='Test news',
            text='Test text'
        )
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.comment = Comment.objects.create( # type: ignore
            news=cls.news,
            author=cls.author,
            text='Test comment'
        )




    @skip('Skipping test_home_page')
    def test_home_page(self):
        # Вызываем метод get для клиента (self.client)
        # и загружаем главную страницу.
        path = reverse('news:home')
        response = self.client.get(path)
        # Проверяем, что код ответа равен 200.
        self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore

    @skip('Skipping test_news_detail')
    def test_news_detail(self):
        url = reverse('news:detail', kwargs={'pk': self.news.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore

    def test_page_availability(self):
        urls = (
            ('news:home', None),
            ('news:detail', {'pk': self.news.pk}),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, kwargs=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK) # type: ignore

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('news:edit', 'news:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'pk': self.comment.pk})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status) # type: ignore

    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('news:edit', 'news:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, args=(self.comment.id,))
                # Получаем ожидаемый адрес страницы логина, 
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)