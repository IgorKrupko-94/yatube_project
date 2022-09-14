from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import pagination_on_page


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    page_obj = pagination_on_page(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pagination_on_page(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    post_list = (Post.objects.select_related('author', 'group')
                 .filter(author__username=username)
                 )
    page_obj = pagination_on_page(request, post_list)
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    author = User.objects.get(username=post.author)
    context = {
        'post': post,
        'author': author,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', username=new_post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post
                    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related(
        'author', 'group').filter(author__following__user=request.user)
    page_obj = pagination_on_page(request, post_list)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', author)
