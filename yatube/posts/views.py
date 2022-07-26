from django.http import HttpResponse


# Главная страница
def index(request):
    return HttpResponse('Эй, йоу, Альбукерк жжёт! Вы на Главной странице!')


def group_posts(request, slug):
    return HttpResponse(f'Это страница с постами, где будет {slug}!')
