from django.urls import path, include
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/', views.EditPostView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:pk>/', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('comments/', views.CommentView.as_view(), name='comments'),
]
