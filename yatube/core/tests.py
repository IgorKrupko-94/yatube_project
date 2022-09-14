from http import HTTPStatus

from django.test import TestCase


class CorePageTests(TestCase):
    def test_error_page(self):
        """Проверяем, что статус ответа сервера на несуществующую
        страницу 404 и используется корректный шаблон."""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code,
                         HTTPStatus.NOT_FOUND,
                         'status-code страницы неверный')
        self.assertTemplateUsed(response,
                                'core/404.html',
                                msg_prefix='Используется неверный шаблон')
