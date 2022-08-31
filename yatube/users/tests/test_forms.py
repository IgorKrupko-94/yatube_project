from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Проверяем, что валидная форма создаёт нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Irvine',
            'last_name': 'Welsh',
            'username': 'trainspotting',
            'email': 'irvinewelsh2022@yandex.ru',
            'password1': 'Ktnj2022!',
            'password2': 'Ktnj2022!',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:index'),
                             msg_prefix='Редирект '
                                        'работает '
                                        'некорректно'
                             )
        self.assertEqual(User.objects.count(),
                         users_count + 1,
                         'Количество пользователей не изменилось')
        self.assertTrue(
            User.objects.filter(
                first_name='Irvine',
                last_name='Welsh',
                username='trainspotting',
                email='irvinewelsh2022@yandex.ru',
            ).exists(),
            'Нового пользователя не существует'
        )
