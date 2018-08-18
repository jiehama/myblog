from django.shortcuts import get_object_or_404,render
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count

#下面三句没用模板标签时，调用的内容
#from django.contrib.contenttypes.models import ContentType
#from comment.models import Comment
#from comment.forms import CommentForm
from .models import Blog,BlogType

from datetime import datetime
from read_statistics.utils import read_statistics_once_read


# Create your views here.
#定义函数公共的博客传参数据
def get_blog_common_data(request,blog_list_all):
    paginator = Paginator(blog_list_all, settings.EACH_PAGE_NUM)  # 每10页进行分页
    page_num = request.GET.get('page', 1)  # 获取URL页面参数（get请求）
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number  # 获取当前页
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))  # 当前页前后各两页
    # 加上省略号
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:  # 如果页码列表第一页不等于1，把第一页插入列表
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:  # 如果页码列表最后一页不等于最后一页，把最后一页加入列表
        page_range.append(paginator.num_pages)
    #获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.annotate(blog_type_count=Count('blog'))#获取博客类型以及对应类型的数量
    context['blog_dates'] = blog_dates_dict
    return context
def blog_list(request):
    blog_list_all= Blog.objects.all()
    context = get_blog_common_data(request, blog_list_all)
    return  render(request,'blog_list.html',context)


def blogs_with_type(request,blog_type_pk):
    blog_type = get_object_or_404(BlogType,pk=blog_type_pk)
    blog_list_all= Blog.objects.filter(blog_type=blog_type)
    context = get_blog_common_data(request,blog_list_all)
    context['blog_type'] = blog_type
    return render(request,'blog_type.html',context)

def blogs_with_date(request,year,month):
    blog_list_all = Blog.objects.filter(created_time__year=year,created_time__month=month)
    context = get_blog_common_data(request,blog_list_all)
    context['blog_with_date'] = '%s年%s月' % (year,month)
    return render(request,'blogs_with_date.html', context)
def blog_detail(request,blog_pk):
    blog = get_object_or_404(Blog,pk=blog_pk)
    read_cookie_key =read_statistics_once_read(request,blog)
    #没用自定义模板标签时，用的下面这句
    #blog_content_type = ContentType.objects.get_for_model(blog)

    #comments = Comment.objects.filter(content_type=blog_content_type,object_id=blog.pk,parent=None)
    context = {}
    context['blog'] = blog
    context['pre_blog'] =Blog.objects.filter(pk__lt=blog.pk).first()#等号的意思是条件值
    context['next_blog'] =Blog.objects.filter(pk__gt=blog.pk).last()

    #没用自定义模板标签时，用的下面这句
    #context['comments'] =comments.order_by('-comment_time')

    # context['comment_form'] = CommentForm(initial={'content_type':blog_content_type.model,'object_id':blog_pk,'reply_comment_id':0})
    response =render(request,'blog_detail.html',context)#响应
    response.set_cookie(read_cookie_key,'true')#阅读cookie标记
    return response



