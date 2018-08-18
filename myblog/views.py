import datetime
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import get_seven_days_read_data,get_today_hot_data,get_yesterday_hot_data
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from blog.models import Blog

def get_7days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today,read_details__date__gte=date)\
            .values('id','title').annotate(read_num_sum=Sum('read_details__read_num'))\
            .order_by('-read_num_sum')
    return blogs[:7]
def home(request):
    blog_content_type =ContentType.objects.get_for_model(Blog)
    dates,read_nums = get_seven_days_read_data(blog_content_type)
    #设置7天热门博客缓存数据
    hot_blogs_7days = cache.get('hot_blogs_7days')
    if hot_blogs_7days is None:
        hot_blogs_7days = get_7days_hot_blogs()
        cache.set('hot_blogs_7days',hot_blogs_7days,3600)
    context ={}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['7days_hot_blogs'] =get_7days_hot_blogs()
    return render(request,'home.html',context)
