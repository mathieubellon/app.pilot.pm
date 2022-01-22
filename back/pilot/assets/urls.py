from django.conf.urls import url

from pilot.assets import views

urlpatterns = [
    # Vue.js AssetApp pages
    # Don't add a $ at the end of the regex, so we catch all and let the Vue router decide which panel he should open
    url(r'^$', views.assets_app, name='ui_assets_list'),
    url(r'^(?P<asset_pk>\d+)', views.assets_app, name='ui_asset_details'),
]
