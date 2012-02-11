# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.core.exceptions import ObjectDoesNotExist
import gnome_developer_network.api.models as models
from django.http import HttpResponse
from django.db   import IntegrityError
import gnome_developer_network.api.giraffe.ast as ast

def index(request):
	page = "<h1>GLib Functions</h1><ul>"

	for func in models.Function.objects.all():
		rvalue = models.ReturnValue.objects.get(callable_obj = func)

		prototype = rvalue.tn_type.c_type 

		prototype += " " + func.c_identifier + "("
		params = models.Parameter.objects.filter(callable_obj = func).order_by('position')
		for param in params:
			prototype += param.tn_type.c_type
			prototype += " " + param.name + ", "
		prototype += ")"

		page += "<li>%s</li>" % (prototype,)

	page += "<ul>"

	return HttpResponse(page)

def _store_props(db_obj, ast_obj, ast_classes):
	for ast_class in ast_classes:
		for prop in models.PROPERTY_MAPPINS[ast_class]:
			if getattr(ast_obj, prop) == None:
				continue
			setattr(db_obj, prop, getattr(ast_obj, prop))

def _store_namespace (ns):
	try:
		db_ns = models.Namespace.objects.get(name = ns.name)
	#TODO: Catch the right exception for this
	except:
		db_ns = models.Namespace()

	_store_props (db_ns, ns, (ast.Namespace,))
	db_ns.save()

	return db_ns
	
def _store_type (ast_type, db_ns):
	try:
		db_type = models.Type.objects.get(c_type = ast_type.c_type)
	except ObjectDoesNotExist:
		db_type = models.Type()
		db_type.namespace = db_ns
		_store_props (db_type, ast_type, (ast.Node, ast.Type))
		db_type.save()

	return db_type

def _store_param (param, position, db_ns, callable_obj):
	db_param = models.Parameter()
	db_param.tn_type = _store_type (param.get_type(), db_ns)
	db_param.position = position
	db_param.callable_obj = callable_obj
	db_param.namespace = db_ns
	_store_props (db_param, param, (ast.TypedNode, ast.Parameter))
	db_param.save()

	return db_param

def _store_return_value (rvalue, db_ns, callable_obj):
	db_rvalue = models.ReturnValue()
	_store_props (db_rvalue, rvalue, (ast.TypedNode,))
	db_rvalue.tn_type = _store_type (rvalue.get_type(), db_ns)
	db_rvalue.callable_obj = callable_obj
	db_rvalue.namespace = db_ns
	db_rvalue.save()

	return db_rvalue

def _store_generic_callable (clble, db_ns, model, asts):
	try:
		db_clble = model.objects.get(c_identifier = clble.c_identifier)
	except ObjectDoesNotExist:
		db_clble = model()
		_store_props (db_clble, clble, asts)
		db_clble.namespace = db_ns
		db_clble.save()

		_store_return_value (clble.return_value, db_ns, db_clble)

		db_params = []
		pos = 0
		for param in clble.parameters:
			db_params.append(_store_param(param, pos, db_ns, db_clble))
			pos += 1

		return db_clble

	#TODO: Update Callable
	return db_clble

def _store_function (fn, db_ns):
	return _store_generic_callable (fn, db_ns, models.Function, (ast.Callable, ast.Node))

def _store_callback (cb, db_ns, parent):
	db_cb = _store_generic_callable (cb, db_ns, models.Callback, (ast.Callable, ast.Node))
	db_cb.callback_of = parent
	db_cb.save()

def _store_method (cb, db_ns, parent):
	classes = (ast.Method, ast.Callable, ast.Node)
	db_method = _store_generic_callable (cb, db_ns, models.Method, classes)
	db_method.method_of = parent
	db_method.save()

def _store_signal (cb, db_ns):
	return _store_generic_callable (cb, db_ns, models.Signal, (ast.Callback, ast.Node))

def _store_value (val, db_ns, parent):
	try:
		db_val = models.Value.objects.get(val = val.value, name = val.name)
	except ObjectDoesNotExist:
		db_val = models.Value()
		db_val.value_of = parent
		_store_props (db_val, val, (ast.Node,))
		db_val.val = val.value
		db_val.namespace = db_ns
		db_val.save()

	return db_val

def _store_enum (enum, db_ns, is_bitfield=False):
	try:
		db_enum = models.Enumeration.objects.get(c_type = enum.c_type)
	except ObjectDoesNotExist:
		db_enum = models.Enumeration()
		_store_props (db_enum, enum, (ast.Node, ast.Type))
		db_enum.is_bitfield = is_bitfield
		db_enum.namespace = db_ns
		db_enum.save()

		for member in enum.members:
			_store_value (member, db_ns, db_enum)


	return db_enum

def _store_field (field, db_ns, parent):
	pass

def _store_record (record, db_ns):
	print record.name
	try:
		db_record = models.Record.objects.get(c_type = record.c_type)
	except:
		db_record = models.Record()
		_store_props (db_record, record, (ast.Node, ast.Type, ast.Record))
		db_record.namespace = db_ns
		db_record.save()

	return db_record
	
def parse(request):
	repo = ast.Repository()
	repo.add_gir ("/usr/share/gir-1.0/GLib-2.0.gir")
#	repo.add_gir ("/usr/share/gir-1.0/GObject-2.0.gir")
#	repo.add_gir ("/usr/share/gir-1.0/Gio-2.0.gir")
	repo.link()

	for ns in repo.namespaces:
		db_ns = _store_namespace (ns)
		#for fn in ns.functions:
		#	_store_function (fn, db_ns)
		#for enum in ns.enumerations:
		#	_store_enum (enum, db_ns, isinstance(enum, ast.BitField))
		for record in ns.records:
			db_record = _store_record (record, db_ns)
			for field in record.fields:
				_store_field (field, db_ns, db_record)
			for callback in record.callbacks:
				_store_callback (callback, db_ns, db_record)
			for method in record.methods:
				_store_method (method, db_ns, db_record)

	return HttpResponse("GIR to SQL transfusion completed")
