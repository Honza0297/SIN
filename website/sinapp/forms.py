from django import forms

choices = (
	("white", "White"),
	("red", "Red"),
	("green", "Green"),
	("blue", "Blue"), # TODO more?
	)

percentages = (
	("0","0%"),
	("10","10%"),
	("20","20%"),
	("30","30%"),
	("40","40%"),
	("50","50%"),
	("60","60%"),
	("70","70%"),
	("80","80%"),
	("90","90%"),
	("100","100%"),
	)


class RGBForm(forms.Form):
	state = forms.BooleanField(required=False, widget= forms.CheckboxInput(attrs={"data-toggle":"toggle"}))
	color = forms.ChoiceField(required=True, choices = choices)

class DimmerForm(forms.Form):
	state = forms.BooleanField(required=False, widget= forms.CheckboxInput(attrs={"data-toggle":"toggle"}))
	intensity = forms.ChoiceField(required=True, choices = percentages)