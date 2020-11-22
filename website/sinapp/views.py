from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormMixin

from django.views.generic import TemplateView

class SINView(TemplateView):
	template_name="templates/home.html"

	def post(self, request, *args, **kwargs):
		return render(template_name)

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)