from http import HTTPStatus
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Анонимный пользователь
        cls.guest_client = Client()
        # Автор поста
        cls.user_author = User.objects.create_user(username='user_author')
        cls.author = Client()
        cls.author.force_login(cls.user_author)
        # Авторизованный пользователь
        cls.test_user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date=datetime.now(),
            author=cls.user_author,
            group=cls.group,
        )

    def test_guest_client_urls_status_code(self):
        """Проверяем status_code у неавторизованного пользователя."""
        urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': 'not_exist_slug'}
                    ): HTTPStatus.NOT_FOUND,
            reverse('posts:profile',
                    kwargs={'username': self.user_author}
                    ): HTTPStatus.OK,
            reverse('posts:profile',
                    kwargs={'username': 'not_exist_author'}
                    ): HTTPStatus.NOT_FOUND,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in urls_code.items():
            with self.subTest(address=address):
                status_code = PostURLTests.guest_client.get(
                    address).status_code
                self.assertEqual(status_code, code, 'Ошибка в status_code')

    def test_guest_client_urls_redirect(self):
        """Проверяем, что страницы /create/ и /posts/<post_id>/edit/
        перенаправят анонимного пользователя на страницу /auth/login/."""
        url_names = {
            reverse('posts:post_create'):
                '/auth/login/?next=/create/',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                f'/auth/login/?next=/posts/{self.post.id}/edit/'
        }
        for address, redirect in url_names.items():
            with self.subTest(address=address):
                response = PostURLTests.guest_client.get(address, follow=True)
                self.assertRedirects(response,
                                     redirect,
                                     msg_prefix=('Перенаправление'
                                                 ' работает'
                                                 ' некорректно')
                                     )

    def test_authorized_client_urls_status_code(self):
        """Проверяем status_code у авторизованного пользователя."""
        urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': 'not_exist_slug'}
                    ): HTTPStatus.NOT_FOUND,
            reverse('posts:profile',
                    kwargs={'username': self.user_author}
                    ): HTTPStatus.OK,
            reverse('posts:profile',
                    kwargs={'username': 'not_exist_author'}
                    ): HTTPStatus.NOT_FOUND,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in urls_code.items():
            with self.subTest(address=address):
                status_code = PostURLTests.authorized_client.get(
                    address).status_code
                self.assertEqual(status_code, code, 'Ошибка в status_code')

    def test_authorized_client_urls_redirect(self):
        """Проверяем, что страница /posts/<post_id>/edit/ перенаправит
        авторизованного пользователя на страницу /posts/<post_id>/."""
        response = PostURLTests.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}), follow=True)
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/',
            msg_prefix='Перенаправление работает некорректно'
        )

    def test_author_urls_status_code(self):
        """Проверяем status_code у автора поста."""
        urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': 'not_exist_slug'}
                    ): HTTPStatus.NOT_FOUND,
            reverse('posts:profile',
                    kwargs={'username': self.user_author}
                    ): HTTPStatus.OK,
            reverse('posts:profile',
                    kwargs={'username': 'not_exist_author'}
                    ): HTTPStatus.NOT_FOUND,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): HTTPStatus.OK,
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in urls_code.items():
            with self.subTest(address=address):
                response = PostURLTests.author.get(
                    address).status_code
                self.assertEqual(response, code, 'Ошибка в status_code')

    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует корректный шаблон."""
        url_template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user_author}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in url_template_names.items():
            with self.subTest(address=address):
                response = PostURLTests.author.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    msg_prefix='Используется некорректный шаблон'
                )
