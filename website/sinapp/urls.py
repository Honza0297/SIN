from django.urls import path, re_path


from .views import SINView

app_name = 'chat'
urlpatterns = [
    path("", SINView.as_view(template_name="templates/home.html")),
 
]