from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=test_user,
            text='Тестовый пост, который будет проверен'
        )

    def test_post_str_model(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(str(post),
                         expected_object_name,
                         'Метод __str__ работает некорректно'
                         )

    def test_post_text_model(self):
        """Проверяем, что у модели Post поле text обрезается до 15 символов,
        при вызове метода __str__."""
        post = PostModelTest.post
        post_text = post.text[:15]
        self.assertEqual(post_text,
                         'Тестовый пост, ',
                         'Поле text обрезается некорректно'
                         )

    def test_post_verbose_name(self):
        """Проверяем, что у модели Post поле verbose_name
        совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verbose_name = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name,
                    expected,
                    'verbose_name отображается некорректно'
                )

    def test_help_text(self):
        """Проверяем, что у модели Post поле help_text
        совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text,
                    expected,
                    'help_text отображается некорректно'
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

    def test_group_str_model(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(str(group),
                         expected_object_name,
                         'Метод __str__ работает некорректно'
                         )

    def test_group_title_model(self):
        """Проверяем, что у модели Group при вызове метода __str__
        выводится поле title."""
        group = GroupModelTest.group
        group_title = group.title
        self.assertEqual(group_title,
                         'Тестовая группа',
                         'Ошибка при вызове метода __str__'
                         )
