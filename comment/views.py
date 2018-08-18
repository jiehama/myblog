from django.shortcuts import render,redirect
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse #异步传输ajax用
from django.urls import reverse
from .models import Comment
from .forms import CommentForm

# Create your views here.
def update_comment(request):
    referer = request.META.get('HTTP_REFERER',reverse('home'))
    comment_form = CommentForm(request.POST,user=request.user)#实例化CommentForm
    if comment_form.is_valid():#验证如果comment_form有效进行下一步操作
        # 检查通过，保存数据
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user

        comment.save()

        #发送邮件通知,comment/models里send_mail方法
        comment.send_mail()

        #不用ajax如此返回 return redirect(referer)
        #用ajax方式返回数据
        data = {}
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.get_nickname_or_username()
        data['comment_time'] = comment.comment_time.timestamp()
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
        return JsonResponse(data)
    else:
    #不用ajax如此返回 return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data = {}
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
        return JsonResponse(data)

    '''没有用forms时的处理方法
    referer = request.META.get('HTTP_REFERER',reverse('home'))
    #数据检查
    if not request.user.is_authenticated:
        return render(request,'error.html',{'message':'您还未登录，请先登录','redirect_to':referer})
    text = request.POST.get('text','').strip()
    if text == '':
        return render(request,'error.html',{'message':'请输入评论内容','redirect_to':referer})

    try:
        content_type = request.POST.get('content_type', '')
        object_id = int(request.POST.get('object_id', ''))
        model_class = ContentType.objects.get(model=content_type).model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except Exception as e:
        return render(request, 'error.html', {'message': '评论系统错误','redirect_to':referer})
    #检查通过，保存数据
    comment = Comment()
    comment.user = request.user
    comment.text = text
    comment.content_object = model_obj
    comment.save()
    return redirect(referer)'''