from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_locations(self):
        """Проверка доступности адресов статичных страниц."""
        urls_code = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for address, code in urls_code.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address).status_code
                self.assertEqual(response, code, 'Ошибка в status_code')

    def test_about_urls_uses_correct_template(self):
        """Проверка корректности шаблонов для статичных страниц."""
        urls_template_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for address, template in urls_template_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response,
                                        template,
                                        msg_prefix=('Используется'
                                                    ' некорректный'
                                                    ' шаблон')
                                        )
