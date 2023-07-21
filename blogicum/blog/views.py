from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import TemplateView, CreateView, DeleteView
from django.urls import reverse_lazy
from .forms import PostForm, CommentForm
from .models import Post, Category, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User


class IndexView(View):
    template_name = 'blog/index.html'

    def get(self, request):
        post_list = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-created_at')

        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'page_obj': page_obj}
        return render(request, self.template_name, context)

class PostDetailView(View):
    template_name = 'blog/detail.html'

    def get(self, request, post_id):
        post = get_object_or_404(
            Post.objects.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
                pk=post_id
            )
        )
        form = CommentForm()
        context = {'post': post, 'form': form}
        return render(request, self.template_name, context)

    def post(self, request, post_id):
        post = get_object_or_404(
            Post.objects.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
                pk=post_id
            )
        )
        form = CommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)

        context = {'post': post, 'form': form}
        return render(request, self.template_name, context)

class CategoryPostsView(View):
    template_name = 'blog/category.html'

    def get(self, request, category_slug):
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        category_list = Post.objects.select_related(
            'category',
            'author',
            'location'
        ).filter(
            is_published=True,
            category__slug=category_slug,
            pub_date__lte=timezone.now()
        )

        paginator = Paginator(category_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'category': category,
            'page_obj': page_obj
        }
        return render(request, self.template_name, context)

class ProfileView(View):
    template_name = 'blog/profile.html'

    def get(self, request, username):
        user = get_object_or_404(User, username=username)

        post_list = Post.objects.filter(
            is_published=True,
            author=user,
            pub_date__lte=timezone.now()
        ).order_by('-created_at')

        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'user': user, 'page_obj': page_obj}
        return render(request, self.template_name, context)

class CreatePostView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

class EditPostView(LoginRequiredMixin, View):
    template_name = 'blog/create.html'

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
        form = PostForm(instance=post)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
        context = {'form': form}
        return render(request, self.template_name, context)

class EditCommentView(LoginRequiredMixin, View):
    template_name = 'blog/edit_comment.html'

    def get(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.author != request.user:
            raise PermissionDenied("You are not allowed to edit this comment.")
        
        form = CommentForm(instance=comment)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.author != request.user:
            raise PermissionDenied("You are not allowed to edit this comment.")
        
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)

        context = {'form': form}
        return render(request, self.template_name, context)

class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/delete_comment.html'
    success_url = reverse_lazy('blog:post_detail')

    def get_object(self, queryset=None):
        comment = super().get_object(queryset=queryset)
        if comment.author != self.request.user:
            raise PermissionDenied
        return comment

class CommentView(TemplateView):
    template_name = 'blog/comments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context
