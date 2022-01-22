from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def assets_app(request, asset_pk=None):
    """Display the main list of Assets objects"""
    return render(request, "main_app.html")
