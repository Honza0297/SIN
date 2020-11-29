from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormMixin

from django.views.generic import TemplateView
import time
from .forms import RGBForm, DimmerForm
from .lights import LEDPublisher

# Generally speaking, global variable is not neccessary here
# but it simplifies things if there were two or more views (in the future?)
pub = LEDPublisher()

 """
 This view controlls main SIN dashboard and makes actions according to the data
 from forms. 
 """
def SINView(request, *args, **kwargs):
	template_name="templates/home.html"

	if request.method == "POST":
		if "rgb" in request.POST:
			form_dimmer = DimmerForm()
			form_rgb = RGBForm(request.POST)
			if form_rgb.is_valid():
				data = form_rgb.cleaned_data
				print("RGB form data:",data)
				# Sending MQTT command here
				pub.rgb_command("on" if data["state"] else "off")
				time.sleep(0.1)
				pub.rgb_command(data["color"])
		elif "dimmer" in request.POST:
			form_rgb = RGBForm()
			form_dimmer = DimmerForm(request.POST)
			if form_dimmer.is_valid():
				data = form_dimmer.cleaned_data
				print("DimmerForm form data:",data)
				pub.dimmer_command(data["intensity"])
	else:
		form_dimmer = DimmerForm()
		form_rgb = RGBForm()


	ctx = {"form_rgb": form_rgb,
		"form_dimmer": form_dimmer}
	return render(request, template_name, ctx)