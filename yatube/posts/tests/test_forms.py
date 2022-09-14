import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.test_client = Client()
        self.test_client.force_login(self.test_user)

    def test_create_post(self):
        """Проверяем, что валидная форма создаёт пост."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
            'image': uploaded
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
            group=PostFormTests.group,
            image='posts/small.gif'
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
            group=self.group,
        ).exists())

    def test_create_comment(self):
        """Проверяем, что после успешной отправки новый комментарий
        появляется на странице поста."""
        comment_count = Comment.objects.count()
        post = Post.objects.create(
            text='Текст для комментирования',
            author=self.test_user
        )
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.test_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id}),
            msg_prefix='Перенаправление работает некорректно'
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1,
            'Количество комментариев не изменилось'
        )
        self.assertTrue(Comment.objects.filter(
            text='Тестовый комментарий'
        ).exists())
