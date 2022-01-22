from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def channels_app(request, tab='active', channel_pk=None):
    return render(request, "main_app.html")
