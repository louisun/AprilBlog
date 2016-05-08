import datetime
import re
import os
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile

from unidecode import unidecode

# delete md_file before delete/change model
from django.db.models.signals import pre_delete
from django.dispatch import receiver


# get gfm html and store it
import requests
from django.core.files.base import ContentFile

upload_dir = 'content/BlogPost/%s/%s'


class Blog(models.Model):
    def get_upload_md_name(self, filename):
        if self.publish_time:
            year = self.publish_time.year
        else:
            year = datetime.now().year
        upload_to = upload_dir % (year, self.title + '.md')

        return upload_to

    def get_html_name(self, filename):
        if self.publish_time:
            year = self.publish_time.year
        else:
            year = datetime.now().year
        upload_to = upload_dir % (year, filename)
        return upload_to

    STATUS_CHOICE = (
        ('d', '草稿'),
        ('p', '发布')
    )

    title = models.CharField('标题', max_length=150, db_index=True, unique=True, blank=True)
    link = models.CharField('链接', max_length=150,  blank=True)
    link.help_text = "Cool URLs don't change"

    snippet = models.TextField('摘要', blank=True)
    content = models.TextField('内容', blank=True)

    add_time = models.DateTimeField('创建时间', auto_now_add=True)
    publish_time = models.DateTimeField('发布时间')
    update_time = models.DateTimeField('修改时间', blank=True)

    status = models.CharField('状态', max_length=1, choices=STATUS_CHOICE, default=STATUS_CHOICE[1][0])

    is_public = models.BooleanField('公开', default=True)
    is_top = models.BooleanField('置顶', default=False)

    access_count = models.IntegerField('浏览量', default=1, editable=False)

    tags = models.ManyToManyField('Tag', verbose_name='标签集合', blank=True)
    tags.help_text = '标签'

    author = models.ForeignKey(User, default='louisun', verbose_name='作者')

    md_file = models.FileField(upload_to=get_upload_md_name, blank=True)

    html_file = models.FileField(upload_to=get_html_name, blank=True)

    @property
    def filename(self):
        if self.md_file:
            return os.path.basename(self.title)
        else:
            return 'no md_file'

    # 保存时调用
    def save(self, *args, **kwargs):
        # 链接标准化

        self.link = slugify(unidecode(self.title))
        # 若无填写 snippet, 自动根据 content 生成摘要

        if not self.content and self.md_file:
            self.content = self.md_file.read()


        if not self.snippet:
        # 若没有snippet, 要生成snippet

            if type(self.content) == bytes:  # sometimes body is str sometimes bytes...
                content = self.content.decode('utf-8')
            elif type(self.content) == str:
                content = self.content
            else:
                print("somthing is wrong")

            # re must be str
            res = re.search('(.*?)<!-- more -->', content, re.S)
            if res:
                snippet = res.group(1)
            else:
                snippet = self.content

            headers = {'Content-Type': 'text/plain'}

            if type(snippet) == bytes:  # sometimes body is str sometimes bytes...
                data = snippet
            elif type(snippet) == str:
                data = snippet.encode('utf-8')
            else:
                print("somthing is wrong")

            r = requests.post('https://api.github.com/markdown/raw', headers=headers, data=data)
            self.snippet = r.text.encode('utf-8')

        # 若只是浏览数更新, 不做其他操作
        modified = kwargs.pop('modified', True)
        # 若文章修改过了, 则更新 update_time
        if modified:
            self.update_time = datetime.datetime.utcnow()

            # 内容更新过了, 由 md 内容重新获得 html 文本并写入
            headers = {'Content-Type': 'text/plain'}

            if type(self.content) == bytes:  # sometimes body is str sometimes bytes...
                data = self.content
            elif type(self.content) == str:
                data = self.content.encode('utf-8')
            else:
                print("somthing is wrong")

            r = requests.post('https://api.github.com/markdown/raw', headers=headers, data=data)
            # avoid recursive invoke
            self.html_file.save(self.title + '.html', ContentFile(r.text.encode('utf-8')), save=False)
            self.html_file.close()



        super(Blog, self).save(*args, **kwargs)

    def display_html(self):
        with open(self.html_file.path, encoding='utf-8') as f:
            return f.read()

    # 获取文章详细页面的绝对路径
    def get_absolute_url(self):
        # 获取 namespace: name 对应的 url
        return reverse('blog:blog_detail', args=(self.id, self.link))

    def __str__(self):
        return self.title


@receiver(pre_delete, sender=Blog)
def blogpost_delete(instance, **kwargs):
    if instance.md_file:
        instance.md_file.delete(save=False)
    if instance.html_file:
        instance.html_file.delete(save=False)


class Tag(models.Model):
    title = models.CharField('标签名', max_length=50, db_index=True, unique=True)

    # 对 Tag 名进行标准化
    def save(self, *args, **kwargs):
        self.title = re.sub('\s', '', self.title)
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class GithubHookSecret(models.Model):
    secret = models.CharField(max_length=255)
