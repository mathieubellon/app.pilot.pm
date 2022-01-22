import json

from django.http import HttpResponse
from django.shortcuts import _get_queryset
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext as _

from pilot.social import post_on_facebook
from pilot.social import post_on_twitter

#
# @login_required
# def tweet_item_publish(request, item_pk):
#     """ Publish a tweet instantly and saves it with the current datetime."""
#
#     desk = request.desk
#     item = get_object_or_404(
#         Item.publishable_tweets.on_demand(),
#         pk=item_pk,
#         desk=desk
#     )
#
#     if request.method == 'POST' and request.POST.get('action') == 'publish':
#         success, error = post_on_twitter(item, check_publication_dt=False, user=request.user)
#         if success:
#             messages.success(request, _("Le tweet a été publié."))
#             item.publication_dt = timezone.now()
#             item.save()
#         else:
#             error_message = ",".join(["'%s'" % el['message'] for el in error])
#             messages.error(request, _("Ce contenu n' a pas pu être publié :  ") + error_message)
#     return HttpResponseRedirect(reverse('ui_item_details', args=[item.pk]))
#
#
# @login_required
# def facebook_item_publish(request, item_pk):
#     """ Publishes a facebook status instantly and saves it with the current datetime."""
#
#     desk = request.desk
#     item = get_object_or_404(
#         Item.publishable_facebook_statuses.on_demand(),
#         pk=item_pk,
#         desk=desk
#     )
#
#     if request.method == 'POST' and request.POST.get('action') == 'publish':
#         success, error = post_on_facebook(item, check_publication_dt=False, user=request.user)
#
#         if success:
#             messages.success(request, _("Le statut a été publié sur facebook."))
#             item.publication_dt = timezone.now()
#             item.save()
#         else:
#             message = _("Ce contenu n' a pas pu être publié :  ")
#             reason_list = [m.get('message') for m in error]
#             message += " ".join(reason_list)
#             messages.error(request, message)
#     return HttpResponseRedirect(reverse('ui_item_details', args=[item.pk]))
#
#
#
# def get_object_or_json_response(klass, *args, **kwargs):
#     """
#     Uses get() to return a tuple (object, HttpResponse). If object does not exist, the HttpResponse contains
#      a json message ready to be sent.
#
#     klass may be a Model, Manager, or QuerySet object. All other passed
#     arguments and keyword arguments are used in the get() query.
#
#     Response optional kwarg must be a dict
#
#     """
#     queryset = _get_queryset(klass)
#     response = kwargs.get('response', {'result': 'error', 'message': 'Item not found'})
#     distinct = kwargs.pop('distinct', True)
#     try:
#         if distinct:
#             return queryset.distinct().get(*args, **kwargs), None
#         else:
#             return queryset.get(*args, **kwargs), None
#         # return queryset.get(*args, **kwargs), None
#     except queryset.model.DoesNotExist:
#         return None, HttpResponse(json.dumps(response), content_type="application/json")
#
#
# @login_required
# def ajax_item_publish_button(request, item_pk):
#     desk = request.desk
#
#     item, json_response = get_object_or_json_response(Item, pk=item_pk, desk=desk)
#     if not item:
#         return json_response
#
#     return render(request, "items/item/ajax/ajax_instant_publish_button.html", {'item': item})
#
#
# @login_required
# def ajax_item_publish_form(request, item_pk):
#     desk = request.desk
#
#     item, json_response = get_object_or_json_response(Item, pk=item_pk, desk=desk)
#     if not item:
#         return json_response
#
#     return render(request, "items/item/ajax/ajax_instant_publish_form.html", {'item': item})


#
# # Twitter views
#
# @login_required
# @perms_utils.editor_required
# def twitter_credentials_details(request, credentials_pk, template_name="twitter/detail.html"):
#     desk = request.desk
#
#     credentials = get_object_or_404(TwitterCredential, pk=credentials_pk, channel__desk=desk)
#
#     context = {'credentials': credentials}
#     return render(request, template_name, context)
#
#
# @login_required
# @perms_utils.admin_required
# def twitter_credentials_delete(request, credentials_pk, template_name="twitter/delete.html"):
#     """Twitter credentials deletion"""
#
#     desk = request.desk
#
#     credentials = get_object_or_404(TwitterCredential, pk=credentials_pk, channel__desk=desk)
#
#     if request.method == 'POST' and request.POST.get('action') == 'delete':
#         with transaction.atomic():
#             create_activity(
#                 actor=request.user,
#                 desk=desk,
#                 verb=Activity.VERB_DELETED,
#                 target=credentials.channel,
#                 action_object=credentials,
#                 action_object_str=_("Token de canal {token}").format(token=credentials)
#             )
#
#             credentials.delete()
#
#         messages.success(request, _("Opération réussie! Le token a été supprimé."))
#         return HttpResponseRedirect(reverse('ui_channels_list'))
#
#     context = {'credentials': credentials}
#     return render(request, template_name, context)
#
#
# @login_required
# @perms_utils.admin_required
# def create_twitter_token(request, credentials_pk):
#     desk = request.desk
#
#     twitter_credential = get_object_or_404(TwitterCredential, pk=credentials_pk, channel__desk=desk)
#     slug = reverse_lazy('ui_twitter_token_verify', args=[twitter_credential.pk])
#     callback_url = get_fully_qualified_url(slug)
#     auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, callback_url)
#
#     try:
#         redirect_url = auth.get_authorization_url()
#     except tweepy.TweepError, e:
#         logging.getLogger('pilot').error('Creation Token impossible :: {0}'.format(e))
#         messages.error(request, _("Nous n'avons pas pu connecter votre canal : {0}".format(e)))
#         return HttpResponseRedirect(reverse('ui_twitter_credentials_detail', args=[twitter_credential.id]))
#     request.session['twitter_request_token'] = (auth.request_token.key, auth.request_token.secret)
#
#     return HttpResponseRedirect(redirect_url)
#
#
# @login_required
# @perms_utils.editor_required
# def verify_token(request, credentials_pk):
#     desk = request.desk
#
#     twitter_credentials = get_object_or_404(TwitterCredential, pk=credentials_pk, channel__desk=desk)
#
#     verifier = request.GET.get('oauth_verifier')
#
#     auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
#     token = request.session.get('twitter_request_token')
#     auth.set_request_token(token[0], token[1])
#     redirect = reverse('ui_twitter_credentials_detail', args=[twitter_credentials.pk])
#     try:
#         auth.get_access_token(verifier)
#     except tweepy.TweepError:
#         messages.error(request, _("Échec, ce token n'est pas autorisé."))
#         return HttpResponseRedirect(redirect)
#
#     twitter_credentials.access_token_key = auth.access_token.key
#     twitter_credentials.access_token_secret = auth.access_token.secret
#     twitter_credentials.save()
#     del request.session['twitter_request_token']
#     messages.success(request, _("Ok, compte connecté !"))
#
#     return HttpResponseRedirect(redirect)
#
#
# @login_required
# @perms_utils.editor_required
# def check_token_valid(request, credentials_pk, template_name="twitter/check_validity.html"):
#     desk = request.desk
#
#     twitter_credentials = get_object_or_404(TwitterCredential, pk=credentials_pk, channel__desk=desk)
#
#     auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
#     auth.set_access_token(twitter_credentials.access_token_key, twitter_credentials.access_token_secret)
#     api = tweepy.API(auth)
#
#     try:
#         validity = api.verify_credentials()
#     except tweepy.TweepError:
#         validity = False
#     context = {'channel': twitter_credentials.channel, 'credentials': twitter_credentials, 'validity': validity}
#
#     return render(request, template_name, context)
#
#
# # Facebook views
#
# @login_required
# @perms_utils.editor_required
# def facebook_credentials_detail(request, credentials_pk, template_name="facebook/detail.html"):
#     desk = request.desk
#
#     credentials = get_object_or_404(FacebookCredential, pk=credentials_pk, channel__desk=desk)
#
#     context = {'credentials': credentials}
#     return render(request, template_name, context)
#
#
# @login_required
# @perms_utils.admin_required
# def facebook_credentials_delete(request, credentials_pk, template_name="facebook/delete.html"):
#     """Facebook credentials deletion"""
#
#     desk = request.desk
#
#     credentials = get_object_or_404(FacebookCredential, pk=credentials_pk, channel__desk=desk)
#
#     if request.method == 'POST' and request.POST.get('action') == 'delete':
#         with transaction.atomic():
#             create_activity(
#                 actor=request.user,
#                 desk=desk,
#                 verb=Activity.VERB_DELETED,
#                 target=credentials.channels,
#                 action_object=credentials,
#                 action_object_str=_("Token de canal {token}").format(token=credentials)
#             )
#
#             credentials.delete()
#
#         messages.success(request, _("Opération réussie! Le token a été supprimé."))
#         return HttpResponseRedirect(reverse('ui_channels_list'))
#
#     context = {'credentials': credentials}
#     return render(request, template_name, context)
#
#
# @login_required
# @perms_utils.admin_required
# def create_facebook_token(request, credentials_pk):
#     desk = request.desk
#
#     get_object_or_404(FacebookCredential, channel__desk=desk, pk=credentials_pk)
#
#     redirect_uri = settings.FACEBOOK_AUTHORIZE_REDIRECT_URI
#     args = {'client_id': settings.FACEBOOK_AUTH_KEY, 'redirect_uri': redirect_uri,
#             'scope': 'publish_actions,manage_pages'}
#     get_url = settings.FACEBOOK_AUTHORIZE_URL + urllib.urlencode(args)
#     request.session['fb_pk'] = credentials_pk
#
#     return HttpResponseRedirect(get_url)
#
#
# @login_required
# @perms_utils.admin_required
# def authorize(request, choose_page=True):
#     desk = request.desk
#
#     redirect_uri = settings.FACEBOOK_AUTHORIZE_REDIRECT_URI
#
#     code = request.GET.get('code')
#
#     credentials_pk = request.session.get('fb_pk')
#     if not credentials_pk:
#         raise Http404
#
#     try:
#         get_token = facebook.get_access_token_from_code(
#             code,
#             redirect_uri=redirect_uri,
#             app_id=settings.FACEBOOK_AUTH_KEY,
#             app_secret=settings.FACEBOOK_AUTH_SECRET
#         )
#     except facebook.GraphAPIError:
#         get_token = {}
#
#     if 'access_token' not in get_token.keys():
#         messages.warning(request, _("La connection n'a pu être effectuée"))
#         return HttpResponseRedirect(
#             reverse('ui_facebook_credentials_detail', kwargs={'credentials_pk': credentials_pk}))
#     access_token = get_token['access_token']
#     if credentials_pk:
#         del request.session['fb_pk']
#
#     fb_credentials = get_object_or_404(FacebookCredential, pk=credentials_pk, channel__desk=desk)
#     on_success_redirect = reverse('ui_facebook_credentials_detail', args=[fb_credentials.pk])
#
#     # Token exchange to get a 2 months valid one
#     api = facebook.GraphAPI(access_token)
#     new_token_response = api.extend_access_token(settings.FACEBOOK_AUTH_KEY, settings.FACEBOOK_AUTH_SECRET)
#     long_token = new_token_response['access_token']
#
#     api = facebook.GraphAPI(long_token)
#     try:
#         user = api.get_object('me')
#         fb_credentials.facebook_id = user.get('id')
#         fb_credentials.facebook_account = user.get('name')
#     except facebook.GraphAPIError:
#         pass
#
#     fb_credentials.access_token = long_token
#     fb_credentials.last_time_checked = timezone.now()
#     fb_credentials.save()
#
#     can_publish = fb_credentials.check_publish_permissions()
#     if fb_credentials.facebook_page_id and fb_credentials.facebook_page_name:
#         if can_publish:
#             messages.success(request, _("Mise à jour de la connexion effectuée avec succès"))
#             return HttpResponseRedirect(on_success_redirect)
#
#     return HttpResponseRedirect(reverse('ui_facebook_choose_page', kwargs={'credentials_pk': credentials_pk}))
#
#
# @login_required
# @perms_utils.admin_required
# def check_facebook_token_valid(request, credentials_pk, template_name="facebook/check_validity.html"):
#     desk = request.desk
#
#     fb_credentials = get_object_or_404(FacebookCredential, pk=credentials_pk, channel__desk=desk)
#
#     validity = fb_credentials.check_validity(save=True)
#
#     can_publish = fb_credentials.check_publish_permissions(save=True)
#
#     context = {
#         'channel': fb_credentials.channel,
#         'credentials': fb_credentials,
#         'validity': validity,
#         'can_publish': can_publish
#     }
#
#     return render(request, template_name, context)
#
#
# @login_required
# @perms_utils.admin_required
# def choose_page(request, credentials_pk, template_name="facebook/choose_page.html"):
#     desk = request.desk
#
#     fb_credentials = get_object_or_404(FacebookCredential, pk=credentials_pk, channel__desk=desk)
#     redirect_url = reverse('ui_facebook_credentials_detail', args=[fb_credentials.pk])
#
#     api = facebook.GraphAPI(fb_credentials.access_token)
#     if request.POST:
#         if request.POST.get('use_feed'):
#             fb_credentials.facebook_type = FacebookCredential.USER_TYPE
#             fb_credentials.save()
#             return HttpResponseRedirect(redirect_url)
#         page_id = request.POST.get('page_id')
#         page_name = request.POST.get('page_name')
#         page_access_token = request.POST.get('page_access_token')
#
#         fb_credentials.facebook_page_id = page_id
#         fb_credentials.facebook_page_name = page_name
#         fb_credentials.facebook_page_token = page_access_token
#         fb_credentials.facebook_type = FacebookCredential.PAGE_TYPE
#         try:
#             fb_credentials.save()
#             return HttpResponseRedirect(redirect_url)
#         except IntegrityError:
#             messages.error(
#                 request,
#                 _("La page sélectionnée ({0}) est déjà associée à une autre chaîne".format(page_name))
#             )
#
#     try:
#         fb_user = api.get_object('me')
#         accounts = api.get_object('me/accounts')
#         data = accounts['data']
#     except facebook.GraphAPIError:
#         data = []
#         fb_user = {}
#
#     return render(request, template_name, {
#         'pages': data,
#         'fb_user': fb_user,
#         'credentials_pk': credentials_pk
#     })
