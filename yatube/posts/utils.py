from django.core.paginator import Paginator

NUMBER_OF_POSTS: int = 10


def pagination_on_page(request, posts_list):
    paginator = Paginator(posts_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
