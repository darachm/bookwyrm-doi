""" manage imports """
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views import View

from bookwyrm import models
from bookwyrm.settings import PAGE_LENGTH


# pylint: disable=no-self-use
@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("bookwyrm.moderate_user", raise_exception=True),
    name="dispatch",
)
class ImportList(View):
    """admin view of imports on this server"""

    def get(self, request, status="active"):
        """list of imports"""
        complete = status == "complete"
        imports = models.ImportJob.objects.filter(complete=complete).order_by(
            "created_date"
        )
        paginated = Paginator(imports, PAGE_LENGTH)
        page = paginated.get_page(request.GET.get("page"))
        data = {
            "imports": page,
            "page_range": paginated.get_elided_page_range(
                page.number, on_each_side=2, on_ends=1
            ),
            "status": status,
        }
        return TemplateResponse(request, "settings/imports/imports.html", data)

    # pylint: disable=unused-argument
    def post(self, request, import_id):
        """Mark an import as complete"""
        import_job = get_object_or_404(models.ImportJob, id=import_id)
        import_job.complete = True
        import_job.save()
        return redirect("settings-imports")
