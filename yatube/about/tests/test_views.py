from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        """Проверяем, что URL генерируемый при помощи namespace доступен."""
        urls_name = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK
        }
        for address, code in urls_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address).status_code
                self.assertEqual(response,
                                 code,
                                 'Ошибка в status_code'
                                 )

    def test_about_pages_uses_correct_template(self):
        """Проверяем, что шаблон получаемый при помощи namespace корректен."""
        urls_template = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for address, template in urls_template.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response,
                                        template,
                                        msg_prefix=('Используется'
                                                    'некорректный'
                                                    'шаблон')
                                        )
