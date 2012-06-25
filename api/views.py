# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.core.exceptions import ObjectDoesNotExist
from giscanner.girparser import GIRParser
import api.models as models
from django.http import HttpResponse
from django.db   import IntegrityError
from django.shortcuts import render_to_response
from storage import GIR_PATH, store_parser
from django.template import Context

def parse(request):
	parser = GIRParser()
	parser.parse(GIR_PATH % "Gtk-3.0")
	store_parser(parser)

	return HttpResponse("<html><head><title>GIR to SQL transfusion completed</title></head><body><h1>GIR to SQL transfusion completed</h1></body></html>")

def index(request):
	namespaces = []
	for db_ns in models.Namespace.objects.all():
		ns = {'name':    db_ns.name,
			  'version': db_ns.version,
			  'classes': False,
			  'methods': False,
			  }
		namespaces.append (ns)

		classes = models.Class.objects.filter (namespace = db_ns)
		for db_class in classes:
			klass = {'name': db_class.gtype_name}
			if not ns['classes']:
				ns['classes'] = []
			ns['classes'].append(klass)

		methods = models.Function.objects.filter(namespace = db_ns)
		for db_methods in methods:
			kethods = {'methods':db_methods.name}
			if not ns['methods']:
				ns['methods'] = []
			ns['methods'].append(kethods)


	ctx = Context({'namespaces': namespaces})
	return render_to_response ('overview.html', ctx)

