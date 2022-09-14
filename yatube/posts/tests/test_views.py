import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, Follow
from ..utils import NUMBER_OF_POSTS

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
COUNT_POSTS_TEST = 17


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='test_user')
        cls.test_client = Client()
        cls.test_client.force_login(cls.test_user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Тестовая группа без постов',
            slug='some_slug',
            description='Тестовое описание для группы без постов',
        )
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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.test_user,
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_pages_uses_correct_template(self):
        """Проверяем, что URL-адрес использует корректный шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.test_user}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_pages_names.items():
            with self.subTest(address=address):
                response = PostPagesTests.test_client.get(address)
                self.assertTemplateUsed(response,
                                        template,
                                        msg_prefix=('Используется'
                                                    ' некорректный'
                                                    ' шаблон'
                                                    ))

    def test_create_post_show_correct_context(self):
        """Проверяем, что шаблон create_post.html
        сформирован с правильным контекстом."""
        response_creation = PostPagesTests.test_client.get(
            reverse('posts:post_create'))
        response_edition = PostPagesTests.test_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field_creation = response_creation.context.get(
                    'form').fields.get(value)
                form_field_edition = response_edition.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field_creation,
                                      expected,
                                      ('Ошибка в переданном контексте'
                                       ' по адресу post_create')
                                      )
                self.assertIsInstance(form_field_edition,
                                      expected,
                                      ('Ошибка в переданном контексте '
                                       'по адресу post_edit')
                                      )

    def post_check_correct(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text,
                             self.post.text,
                             'Ошибка в тексте поста'
                             )
            self.assertEqual(post.author,
                             self.post.author,
                             'Ошибка в авторе поста'
                             )
            self.assertEqual(post.group,
                             self.post.group,
                             'Ошибка в группе поста'
                             )
            self.assertEqual(post.image,
                             self.post.image,
                             'Ошибка в картинке поста'
                             )

    def test_index_page_correct_context(self):
        """Проверяем, что шаблон index.html
        сформирован с правильным контекстом."""
        response = PostPagesTests.test_client.get(
            reverse('posts:index')).context['page_obj']
        for post in response:
            self.post_check_correct(post)

    def test_group_list_page_correct_context(self):
        """Проверяем, что шаблон group_list.html
        сформирован с правильным контекстом."""
        response = PostPagesTests.test_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ))
        self.assertEqual(response.context['group'],
                         self.group,
                         'В контекст передана некорректная группа'
                         )
        for post in response.context['page_obj']:
            self.post_check_correct(post)

    def test_profile_page_correct_context(self):
        """Проверяем, что шаблон profile.html
        сформирован с правильным контекстом."""
        response = PostPagesTests.test_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.test_user}
                    ))
        self.assertEqual(response.context['author'],
                         self.test_user,
                         'В контекст передан некорректный автор'
                         )
        for post in response.context['page_obj']:
            self.post_check_correct(post)

    def test_post_detail_page_correct_context(self):
        """Проверяем, что шаблон post_detail.html
        сформирован с правильным контекстом."""
        response = PostPagesTests.test_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ))
        self.assertEqual(response.context['author'],
                         self.test_user,
                         'В контекст передан некорректный автор'
                         )
        self.post_check_correct(response.context['post'])

    def test_post_on_pages(self):
        """Проверяем, что тестовый пост с указанной группой
        появляется на главной странице, на странице выбранной группы
        и в профайле пользователя, но не появляется на странице группы,
        для которой не был предназначен."""
        urls_count_posts = {
            reverse('posts:index'): 1,
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): 1,
            reverse('posts:profile', kwargs={'username': self.test_user}): 1,
            reverse('posts:group_list',
                    kwargs={'slug': self.another_group.slug}): 0,
        }
        for address, count in urls_count_posts.items():
            with self.subTest(address=address):
                response = PostPagesTests.test_client.get(
                    address).context['page_obj']
                self.assertEqual(len(response),
                                 count,
                                 ('Ошибка отображения'
                                  ' тестового поста на странице')
                                 )

    def test_cache_index_page(self):
        """Проверяем, что кеширование работает на главной странице."""
        post = Post.objects.create(
            text='Пост для проверки кеша',
            author=self.test_user,
            group=self.group
        )
        post_on_page = PostPagesTests.test_client.get(
            reverse('posts:index')).content
        post.delete()
        post_in_cache = PostPagesTests.test_client.get(
            reverse('posts:index')).content
        self.assertEqual(post_on_page,
                         post_in_cache,
                         'Пост не сохраняется в кеше'
                         )
        cache.clear()
        post_not_on_page = PostPagesTests.test_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(post_on_page,
                            post_not_on_page,
                            'Пост остаётся на странице после очистки кеша')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='test_user')
        cls.test_client = Client()
        cls.test_client.force_login(cls.test_user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(COUNT_POSTS_TEST):
            Post.objects.create(
                text=f'Some post text №{i}',
                author=cls.test_user,
                group=cls.group
            )

    def setUp(self):
        cache.clear()

    def test_pages_of_count_posts(self):
        """Проверяем работу пагинатора на страницах index.html,
        group_list.html и profile.html."""
        url_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.test_user}),
        ]
        for address in url_names:
            with self.subTest(address=address):
                self.assertEqual(
                    len(PaginatorViewsTest.test_client.get(
                        address).context.get('page_obj')),
                    NUMBER_OF_POSTS,
                    'Количество постов на первой странице неверное'
                )
                self.assertEqual(
                    len(PaginatorViewsTest.test_client.get(
                        address + '?page=2').context.get('page_obj')),
                    COUNT_POSTS_TEST - NUMBER_OF_POSTS,
                    'Количество постов на второй странице неверное'
                )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create(username='test_author')
        cls.test_follower = User.objects.create(username='test_follower')
        cls.post = Post.objects.create(
            text='Пост для подписки',
            author=cls.test_author
        )

    def setUp(self):
        cache.clear()
        self.follower = Client()
        self.follower.force_login(self.test_follower)
        self.author = Client()
        self.author.force_login(self.test_author)

    def test_follow_on_user(self):
        """Проверяем, что авторизованный пользователь может подписаться
        на другого пользователя."""
        follow_count = Follow.objects.count()
        self.author.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.test_follower}
            )
        )
        latest_follow = Follow.objects.all().latest('id')
        self.assertEqual(
            Follow.objects.count(),
            follow_count + 1,
            'Количество подписок не изменилось'
        )
        self.assertEqual(
            latest_follow.user.id,
            self.test_author.id,
            'Ошибка в подписчике'
        )
        self.assertEqual(
            latest_follow.author.id,
            self.test_follower.id,
            'Ошибка в авторе'
        )

    def test_unfollow_on_user(self):
        """Проверяем, что авторизованный пользователь может отписаться
        от другого пользователя."""
        Follow.objects.create(
            user=self.test_author,
            author=self.test_follower
        )
        follow_count = Follow.objects.count()
        self.author.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.test_follower}
            )
        )
        self.assertEqual(
            Follow.objects.count(),
            follow_count - 1,
            'Количество подписок не изменилось'
        )

    def test_post_on_page_following(self):
        """Проверяем, что новая запись пользователя появляется в ленте тех,
        кто на него подписан."""
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.test_author
        )
        Follow.objects.create(
            user=self.test_follower,
            author=self.test_author
        )
        response = self.follower.get(reverse('posts:follow_index'))
        self.assertIn(
            post,
            response.context['page_obj'].object_list,
            'Пост не появился на странице подписчика'
        )

    def test_posts_not_on_page_following(self):
        """Проверяем, что новая запись пользователя не появляется
        в ленте тех, кто на него не подписан."""
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.test_author
        )
        response = self.follower.get(reverse('posts:follow_index'))
        self.assertNotIn(
            post,
            response.context['page_obj'].object_list,
            'Пост появляется на странице не подписанного пользователя'
        )
