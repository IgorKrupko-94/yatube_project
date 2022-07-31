from django.shortcuts import render, get_object_or_404
from .models import Post, Group


# Главная страница
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    header = 'Последние обновления на сайте'
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts': posts,
        'title': title,
        'header': header,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    header = 'Лев Толстой - зеркало русской революции.'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'group': group,
        'posts': posts,
        'header': header,
    }
    return render(request, template, context)
