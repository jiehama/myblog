import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone
# Create your models here.

#多线程处理邮件发送
class SendMail(threading.Thread):
    # 初始化传入参数
    def __init__(self,subject,text,email,fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently =fail_silently
        threading.Thread.__init__(self)
    def run(self):
        send_mail(self.subject, '', settings.EMAIL_HOST_USER, [self.email],
                  fail_silently=self.fail_silently,html_message=self.text)

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,related_name='comments',on_delete=models.CASCADE)#外键评论的人

    root = models.ForeignKey('self',related_name='root_comment',null=True,on_delete=models.CASCADE)
    parent= models.ForeignKey('self',null=True,related_name='parent_comment',on_delete=models.CASCADE)#上级ID的主键值，树结构，外键指向评论
    reply_to = models.ForeignKey(User,null=True,related_name='replies',on_delete=models.CASCADE)#回复谁

    #异步发送邮件
    def send_mail(self):
        #发送邮件通知
        if self.parent is None:
            #没有父节点，回复博客
            subject = '[5tiger]有人评论你的博客'#邮件主题
            email = self.content_object.get_email()
        else:
            #有父节点，回复评论
            subject = '[5tiger]有人回复你的评论'#邮件主题
            email = self.reply_to.email
        if email != '':
            # 邮件内容，简单的直接写，复杂了可以用模板
            #text = '%s\n<a href="%s">%s</a>' % (self.text , self.content_object.get_url(),'点击查看')
            context ={}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render_to_string('comment/send_mail.html',context)
            send_mail = SendMail(subject,text,email)#调用多线程方法
            send_mail.start()

    #让评论显示出内容，不只显示object
    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time']