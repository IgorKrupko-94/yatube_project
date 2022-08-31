from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='test_user',
                                            first_name='Тестовый',
                                            last_name='Юзер',
                                            email='test_user2022@yandex.ru'
                                            )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.test_user)

    def test_users_pages_uses_correct_template(self):
        """Проверяем, что URL-адрес использует корректный шаблон."""
        urls_template = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
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
            reverse('users:logout'): 'users/logged_out.html',
        }
        for address, template in urls_template.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response,
                                        template,
                                        msg_prefix=('Используется'
                                                    'некорректный'
                                                    'шаблон'
                                                    )
                                        )

    def test_signup_show_correct_context(self):
        """Проверяем, что шаблон signup.html
        сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field_user = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field_user,
                                      expected,
                                      ('Ошибка в переданном контексте'
                                       'по адресу signup')
                                      )
