import random
from collections import defaultdict
from django.conf import settings
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404, render, redirect
from .models import Blog, Tag
from .libs.tag_cloud import TagCloud

exclude_posts = ("about",)

class TaglistView(generic.ListView):
    template_name = 'tag_list.html'
    # 修改 上下文对象名
    context_object_name = 'tag_list'
    model = Tag

    # 对 tag 的显示进行处理: 中间数据都是临时生成的
    def get_context_data(self, **kwargs):
        context = super(TaglistView, self).get_context_data(**kwargs)
        # 获取 tag 的集合
        tag_list = context.get("tag_list")

        # 有 blog 的 tag
        tag_list_have_blog = []
        for tag in tag_list:
            # 获取这个 tag 的博文数
            blog_count = Blog.objects.filter(tags__pk=tag.id).count()
            if blog_count > 0:
                tag.blog_count = blog_count
                tag_list_have_blog.append(tag)

        # 获取有博文的 tag 中博文数最大和最小的 tag 的博文数
        max_count = max(tag_list_have_blog, key=lambda tag: tag.blog_count).blog_count
        min_count = min(tag_list_have_blog, key=lambda tag: tag.blog_count).blog_count

        tag_cloud = TagCloud(min_count, max_count)

        # 通过 TagCloud 给每个 tag 添加 font_size 和 color 信息
        for tag in tag_list_have_blog:
            tag_font_size = tag_cloud.get_tag_font_size(tag.blog_count)
            color = tag_cloud.get_tag_color(tag.blog_count)
            tag.color = color
            tag.font_size = tag_font_size

        context['tag_list'] = tag_list_have_blog
        return context


class BlogListView(generic.ListView):
    template_name = 'post_list.html'
    paginate_by = settings.PAGE_SIZE
    context_object_name = 'blog_list'

    def get_queryset(self, **kwargs):
        # 只显示状态为发布, 且公开的文章列表
        query_condition = {
            'status': 'p',
            'is_public': True
        }
        # 若指定标签, 只显示改标签的文章列表
        if 'tag_name' in self.kwargs:
            print(self.kwargs)
            query_condition['tags__title'] = self.kwargs['tag_name']
        # 按发布时间倒序排列
        return Blog.objects.exclude(title__in=exclude_posts).filter(**query_condition).order_by('-publish_time')

    def get_context_data(self, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        # 若指定标签, 添加标签的信息 title 和 description
        tag_name = kwargs.get('tag_name')
        if tag_name:
            context['tag_title'] = tag_name
            context['tag_description'] = ''

        return context


class BlogDetailView(generic.DetailView):
    model = Blog
    template_name = 'post_detail.html'

    def get_object(self, queryset=None):
        # 获取对象的时候, 检查权限以及修改对象的内容
        blog = super(BlogDetailView, self).get_object(queryset)
        if blog.status == 'd' or (not blog.is_public and self.request.user != blog.author):
            raise PermissionDenied
        # 流量数量+1, 并且标记为不是更新, 即不更改 update_time
        blog.access_count += 1
        blog.save(modified=False)
        return blog





class ArchiveListView(generic.ListView):
    template_name = 'archive.html'
    context_object_name = 'blog_list'

    def get_queryset(self, **kwargs):
        posts_by_year = defaultdict(list)

        query_condition = {
            'status': 'p',
            'is_public': True
        }

        # 按发布时间倒序排列
        blogs = Blog.objects.exclude(title__in=exclude_posts).filter(**query_condition).order_by('-publish_time')
        for post_blog in blogs:
            year = post_blog.publish_time.year
            posts_by_year[year].append(post_blog)
        posts_by_year = sorted(posts_by_year.items(), reverse=True)
        return posts_by_year




class LatestPosts(Feed):
    """
    RSS输出
    """

    title = "louisun的博客"
    link = '/'

    def items(self):
        blogs = Blog.objects.filter(status='p', is_public=True).all().order_by('-publish_time')[:10]
        return blogs

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.snippet



def about(request):
    the_about_post = get_object_or_404(Blog, title="about")
    args = {"about": the_about_post}
    return render(request, 'about.html', args)