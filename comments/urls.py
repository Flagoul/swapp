from rest_framework.routers import DefaultRouter
from comments.views import CommentViewSet

router = DefaultRouter()
router.register(r"comments", CommentViewSet, base_name="comments")
urlpatterns = router.urls
