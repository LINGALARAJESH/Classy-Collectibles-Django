from django.urls import path,include
from . import views


urlpatterns = [
        path("signin/",views.signin,name="signin"),
        path("login/",views.handlelogin,name="handlelogin"),
        path("logout/",views.handlelogout,name="handlelogout"),
        path("activate/<uidb64>/<token>",views.ActivateAccountView.as_view(),name="activate"),
        path("request-reset-email/",views.RequestRestEmailView.as_view(),name="request-reset-email"),
        path("set-new-password/<uidb64>/<token>",views.SetNewpasswordView.as_view(),name="set-new-password"),
]
