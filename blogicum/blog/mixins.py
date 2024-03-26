from django.shortcuts import redirect
from django.urls import reverse

PAGINATE_BY_THIS = 10


class PaginateMixin:

    paginate_by = PAGINATE_BY_THIS


class DispatchPostMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                reverse("blog:post_detail",
                        kwargs={"post_id": self.kwargs["post_id"]})
            )
        return super().dispatch(request, *args, **kwargs)


class DispatchCommentMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                reverse("blog:post_detail", kwargs={
                        "post_id": self.kwargs["post_id"]})
            )
        return super().dispatch(request, *args, **kwargs)
