from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.test_client = Client()
        self.test_client.force_login(self.test_user)

    def test_create_post(self):
        """Проверяем, что валидная форма создаёт пост."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        response = self.test_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.test_user}
                                     ),
                             msg_prefix='Перенаправление работает некорректно')
        self.assertEqual(Post.objects.count(),
                         post_count + 1,
                         'Количество постов не увеличилось'
                         )
        self.assertTrue(Post.objects.filter(
            text='Новый пост',
            group=PostFormTests.group
        ).exists())

    def test_edit_post(self):
        """Проверяем, что валидная форма редактирует пост."""
        post = Post.objects.create(
            text='Текст для редактирования',
            author=self.test_user
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id
        }
        response = self.test_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id}),
            msg_prefix='Перенаправление работает некорректно'
        )
        self.assertEqual(Post.objects.count(),
                         post_count,
                         'Количество постов изменилось'
                         )
        self.assertTrue(Post.objects.filter(
            text='Отредактированный текст',
            group=self.group
        ).exists())
