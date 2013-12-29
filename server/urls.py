from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'taxiexpress.views.index', name='index'),
    url(r'^client/login', 'taxiexpress.views.loginUser', name='loginUser'),
    url(r'^client/register', 'taxiexpress.views.registerUser', name='registerUser'),
    url(r'^loaddata', 'taxiexpress.views.loadData', name='loaddata'),
    url(r'^test', 'taxiexpress.views.test', name='test'),
    url(r'^client/validate', 'taxiexpress.views.validateUser', name='validateUser'),
    url(r'^client/changedetails', 'taxiexpress.views.updateProfileMobile', name='updateProfileMobile'),
    url(r'^client/changepassword', 'taxiexpress.views.changePassword', name='changePassword'),
    url(r'^client/addfavorite', 'taxiexpress.views.addFavoriteDriver', name='addFavoriteDriver'),
    url(r'^client/removefavorite', 'taxiexpress.views.removeFavoriteDriver', name='removeFavoriteDriver'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # url(r'^server/', include('server.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
