from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Анонимный пользователь
        cls.guest = Client()
        # Авторизованный пользователь
        cls.test_user = User.objects.create_user(username='test_user')
        cls.authorized = Client()
        cls.authorized.force_login(cls.test_user)

    def test_guest_urls_status_code(self):
        """Проверяем status_code у неавторизованного пользователя."""
        urls_code = {
            reverse('users:logout'): HTTPStatus.OK,
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
        }
        for address, code in urls_code.items():
            with self.subTest(address=address):
                response = UserURLTests.guest.get(address).status_code
                self.assertEqual(response, code, 'Ошибка в status_code')

    def test_guest_urls_redirect(self):
        """Проверяем, что анонимный пользователь будет перенаправлен
        на страницу /auth/login/ при попытке входа на недоступные URLs."""
        url_names = {
            reverse('users:password_change'):
                '/auth/login/?next=/auth/password_change/',
            reverse('users:password_change_done'):
                '/auth/login/?next=/auth/password_change/done/',
        }
        for address, redirect in url_names.items():
            with self.subTest(address=address):
                response = UserURLTests.guest.get(address, follow=True)
                self.assertRedirects(response,
                                     redirect,
                                     msg_prefix=('Перенаправление'
                                                 ' работает'
                                                 ' некорректно')
                                     )

    def test_authorized_urls_status_code(self):
        """Проверяем status_code у авторизованного пользователя."""
        urls_code = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_change'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
        }
        for address, code in urls_code.items():
            with self.subTest(address=address):
                response = UserURLTests.authorized.get(address).status_code
                self.assertEqual(response, code, 'Ошибка в status_code')

    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует корректный шаблон."""
        url_template_names = {
            reverse('users:signup'):
                'users/signup.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
        }
        for address, template in url_template_names.items():
            with self.subTest(address=address):
                response = UserURLTests.authorized.get(address)
                self.assertTemplateUsed(response,
                                        template,
                                        msg_prefix=('Используется'
                                                    ' некорректный'
                                                    ' шаблон')
                                        )

    def test_urls_y_logout_uses_correct_template(self):
        """Проверяем, что /logout/ использует корректный шаблон."""
        response = UserURLTests.authorized.get(reverse('users:logout'))
        self.assertTemplateUsed(response,
                                'users/logged_out.html',
                                msg_prefix='Используется некорректный шаблон')

    def test_y_authorized_url_logout_status_code(self):
        """Проверяем status_code на странице /logout/."""
        response = UserURLTests.authorized.get(
            reverse('users:logout')).status_code
        self.assertEqual(response, HTTPStatus.OK, 'Ошибка в status_code')
