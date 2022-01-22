from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request, template_name="main_app.html", tab="dashboard"):
    """Dashboard."""
    return render(request, template_name)
