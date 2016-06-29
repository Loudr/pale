# -*- coding: utf-8 -*-
import datetime
import json
import logging
import sys

import arrow
from pale import config as pale_config
from pale.arguments import BaseArgument
from pale.fields import ResourceField, ListField, ResourceListField
from pale.errors import APIError, ArgumentError, AuthenticationError
from pale.meta import MetaHasFields
from pale.resource import NoContentResource, Resource, DebugResource
from pale.response import PaleRaisedResponse


class PaleDefaultJSONEncoder(json.JSONEncoder):
    """The default JSON Encoder for Pale.

    The main difference between this and Python's default JSON encoder
    is that this encoder attempts to serialize datetimes to ISO format,
    and tries to call a `to_dict` method on the passed in object before
    giving up.
    """
    def default(self, obj):
        try:
            if isinstance(obj, datetime.datetime):
                # do the datetime thing,  or
                encoded = arrow.get(obj).isoformat()
            else:
                # try the normal encoder
                encoded = json.JSONEncoder.default(self, obj)
        except TypeError as e:
            # if that fails, check for the to_dict method,
            if hasattr(obj, 'to_dict') and callable(obj.to_dict):
                # and use it!
                encoded = obj.to_dict()
            else:
                raise e
        return encoded


class Endpoint(object):
    __metaclass__ = MetaHasFields

    _response_class = None
    _json_serializer = PaleDefaultJSONEncoder()

    _default_cache = 'no-cache'


    @classmethod
    def _fix_up_fields(cls):
        """Add names to all of the Endpoint's Arguments.

        This method will get called on class declaration because of
        Endpoint's metaclass.  The functionality is based on Google's NDB
        implementation."""
        cls._arguments = {}
        if cls.__module__ == __name__: # skip the classes in this file
            return
        for name in set(dir(cls)):
            attr = getattr(cls, name, None)
            if isinstance(attr, BaseArgument):
                if name.startswith('_'):
                    raise TypeError("Endpoint argument %s cannot begin with "
                            "an underscore, as these attributes are reserved "
                            "for instance variables of the endpoint object, "
                            "rather than for arguments to your HTTP Endpoint."
                            % name)
                attr._fix_up(cls, name)
                cls._arguments[attr.name] = attr


    def _set_response_class(self, response_class):
        """Sets the response class for this endpoint.  This is usually only
        called by the Pale adapter, and intended to be called with the Response
        object of the HTTP layer that you're using."""
        self._response_class = response_class


    @classmethod
    def _set_json_serializer(cls, serializer):
        cls._json_serializer = serializer


    @classmethod
    def _metadata(cls, *args, **kwargs):
        return dict(**kwargs)


    def _handle(self, context):
        """The meat of the API logic.  This method is intended to be overridden
        by subclasses, and should perform the core logic of the API method in
        question.
        """
        pass


    def _execute(self, request, **kwargs):
        """The top-level execute function for the endpoint.  This method is
        intended to remain as-is, and not be overridden.  It gets called by
        your HTTP framework's route handler, and performs the following actions
        to process the request:

        ``authenticate_request``
            Validate the Bearer token, populate the ``current_user``, and make
            sure that the token covers the scope needed to call the requested
            method.
                         *
                         *
        ``parse arguments``
            The argument parser is responsible for:
              - First, coercing and patching any parameters that might require
                it due to versioning (i.e. the caller is using an old API
                version that supports `index` as a parameter for pagination,
                but the current version uses the name `offset`)
              - Second, iterating through the endpoint's supported arguments
                and validating that the params passed in comply with the
                endpoint's requirements
              - Third, populating the `context.args` array with the validated
                arguments
            If any of the arguments are invalid, then the Argument parser will
            raise an ArgumentError that bubbles up to the `try/catch` block of
            the execute method.
                         *
                         *
        ``before handler``
            The before_handlers are specified by the Endpoint definition, and
            are intended to supporty DRY-ing up your codebase.  Have a set of
            Endpoints that all need to grab an object from the ORM based on the
            same parameter?  Make them inherit from an Endpoint subclass that
            performs that task in a before_handler!
                         *
                         *
        ``handle``
            The core logic of your API endpoint, as implemented by you in your
            Endpoint subclass.  The API Framework expects ``handle`` to return
            a dictionary specifying the response object and the JSON key that
            it should hang off of, or a tuple of a dictionary and an HTTP status
            code.
                         *
                         *
        ``after_handler``
            Like the before_handlers, the ``after_handlers`` happen after the
            handle method, and allow the endpoint developer to re-use code for
            post-processing data from an endpoint.
                         *
                         *
        ``render response``
            Like the argument parser, the response renderer is responsible for
            a few things:
              - First, it converts the ORM objects into JSON-serializable
                Python dictionaries using the Resource objects defined by the
                API implementation,
              - Second, it does any version parameter coersion, renaming and
                reformatting the edge version of the response to match the
                version requested by the API caller,
              - and Third, it serializes the Python dictionary into the response
                format requested by the API caller (right now, we only support
                JSON responses, but it'd be reasonble to support something like
                HTML or XML or whatever in the future).
            The rendered JSON text is then returned as the response that should
            be sent by your HTTP framework's routing handler.
                         *
                         *
        ``_after_response_handler``
            The `_after_response_handlers` are sepcified by the Endpoint
            definition, and enable manipulation of the response object before it
            is returned to the client, but after the response is rendered.

            Because these are instancemethods, they may share instance data
            from `self` specified in the endpoint's `_handle` method.

        ``_allow_cors``
            This value is set to enable CORs for a given endpoint.

            When set to a string it supplies an explicit value to
            'Access-Control-Allow-Origin'.

            Set to True, this will allow access from *all* domains;
                Access-Control-Allow-Origin = "*"

        """
        try:
            self._create_context(request)
            self._authenticate()

            self._parse_args()

            if hasattr(self, '_before_handlers') and \
                    isinstance(self._before_handlers, (list, tuple)):
                for handler in self._before_handlers:
                    handler(self._context)

            self._context.handler_result = self._handle(self._context)

            if hasattr(self, '_after_handlers') and \
                    isinstance(self._after_handlers, (list, tuple)):
                for handler in self._after_handlers:
                    handler(self._context)

            self._render()
            response = self._context.response
            # After calling ._render(), the response is ready to go, so we
            # shouldn't need to handle any other exceptions beyond this point.
        except AuthenticationError as e:
            if hasattr(e, 'message') and e.message is not None:
                message = e.message
            else:
                message = "You don't have permission to do that."
            err = APIError.Forbidden(message)
            response = self._response_class(*err.response)
            response.headers["Content-Type"] = 'application/json'
        except ArgumentError as e:
            err = APIError.UnprocessableEntity(e.message)
            response = self._response_class(*err.response)
            response.headers["Content-Type"] = 'application/json'
        except APIError as e:
            response = self._response_class(*e.response)
            response.headers["Content-Type"] = 'application/json'
        except PaleRaisedResponse as r:
            response = self._response_class(*r.response)
            response.headers["Content-Type"] = 'application/json'
        except Exception as e:
            logging.exception(e)
            raise

        allow_cors = getattr(self, "_allow_cors", None)
        if allow_cors is True:
            response.headers['Access-Control-Allow-Origin'] = '*'
        elif isinstance(allow_cors, basestring):
            response.headers['Access-Control-Allow-Origin'] = allow_cors

        try:
            if hasattr(self, '_after_response_handlers') and \
                    isinstance(self._after_response_handlers, (list, tuple)):
                for handler in self._after_response_handlers:
                    handler(self._context, response)
        except Exception as e:
            logging.exception(
                "Failed to process _after_response_handlers for Endpoint %s"
                % self.__class__.__name__)
            raise

        return response


    def _create_context(self, request):
        if pale_config.create_context is None:
            raise ValueError((
                    "\n\nPale does not appear to be configured, as there is no "
                    "context creator currently set!\n\n"))
        self._context = pale_config.create_context(self, request)


    def _authenticate(self):
        if pale_config.authenticate_context is None:
            raise ValueError((
                    "\n\nPale does not appear to be configured, as there is no "
                    "context authenticator currently set!\n\n"))
        pale_config.authenticate_context(self._context)


    def _patch_args(self):
        # do something like:
        # version = self._context.api_version
        # coersion_dict = self.grab_version_coersion_info_from_impl(version)
        # self.patched_args = self.coerce(self._raw_args, coersion_dict)

        # but for now, just push the raw args through
        self._context.patched_args = self._context._raw_args


    def _parse_args(self):
        self._patch_args()

        parsed_args = {}
        if self._arguments is not None:
            if not isinstance(self._arguments, dict):
                raise ValueError("""Your API implementation is broken.  This
                endpoint's `arguments` value is a `%s` when it should be a dict
                instead.  Please see the Pale documentation for information on
                how to fix the problem.""" % (type(self.arguments), ))

            for arg_name, arg_obj in self._arguments.iteritems():
                patched_value = self._context.patched_args.get(arg_name, None)

                # HTTP libraries are crap, so we expect `patched_value` to
                # be a list, which we strip out if the length is 1 and if the
                # validator doesn't expect a list
                if patched_value is not None and \
                        isinstance(patched_value, list) and \
                        len(patched_value) == 1 and \
                        list not in arg_obj.allowed_types:
                    patched_value = patched_value[0]

                # validate will return the validated (and thus valid) value on
                # success, or raise an ArgumentError if the value is invalid
                validated_value = arg_obj.validate(patched_value, arg_name)
                if validated_value is not None:
                    parsed_args[arg_name] = validated_value
        self._context.args = parsed_args


    def _parse_handler_result(self, result):
        """Parses the item(s) returned by your handler implementation.

        Handlers may return a single item (payload), or a tuple that gets
        passed to the Response class __init__ method of your HTTP layer.

        _parse_handler_result separates the payload from the rest the tuple,
        as well as providing the tuple so that it can be re-composed after
        the payload has been run through the `_returns` Resource's renderer.
        """
        if isinstance(result, (list, tuple)):
            payload = result[0]
            list_result = list(result)
        else:
            payload = result
            list_result = [""]
        return payload, list_result


    def _render(self):
        # first, serialize the Python objects in the response_dict into a dict
        rendered_content = {}

        unrendered_content, response_init_list = self._parse_handler_result(
                self._context.handler_result)

        if hasattr(unrendered_content, 'iteritems'):
            for k, v in unrendered_content.iteritems():
                # usually there should only be one key and value here
                dict_val = self._returns._render_serializable(v, self._context)

                # this is where object versioning should be implemented, but
                # one outstanding question with it is, should this be the
                # responsibility of the Resource object, or of the endpoint?

                # coerced_dict_val = self.returns.versionify(dict_val,
                #        self._context.api_version)

                rendered_content[k] = dict_val
        else:
            # maybe it's a nonetype or a simple string?
            rendered_content = self._returns._render_serializable(
                    unrendered_content, self._context)

        # now build the response
        if rendered_content is None and \
                isinstance(self._returns, NoContentResource):
            json_content = ''
        else:
            json_content = self._json_serializer.encode(rendered_content)
        response_init_list[0] = json_content
        response_init_tuple = tuple(response_init_list)
        if self._response_class is None:
            raise ValueError("""Error with Pale configuration.  Attempted to
            parse a handler result without a response class set on the endpoint.
            This is probably an issue with the pale HTTP adapter you're using,
            since that is where the response class is usually set.""")
        self._context.response = self._response_class(*response_init_tuple)

        # patch up cache-control
        updated_cache_ctrl_from_endpoint = False
        if len(response_init_tuple) > 2:
            # headers is the 3rd arg for both flask and webapp2
            headers = response_init_tuple[2]
            cache_ctrl = headers.get('Cache-Control')
            if cache_ctrl is not None:
                self._context.response.headers['Cache-Control'] = cache_ctrl
                updated_cache_ctrl_from_endpoint = True

        if not updated_cache_ctrl_from_endpoint:
            self._context.response.headers['Cache-Control'] = \
                    self._default_cache

        # Add default json response type.
        if len(json_content):
            self._context.response.headers["Content-Type"] = 'application/json'
        else:
            del self._context.response.headers["Content-Type"]


class ResourcePatch(object):
    """Represents a resource patch which is to be applied
    to a given dictionary or object."""

    def __init__(self, patch, resource, ignore_missing_fields=False):
        self.patch = patch
        self.resource = resource
        self.ignore_missing_fields = ignore_missing_fields

    def get_field_from_resource(self, field):
        if isinstance(self.resource, DebugResource):
            # no fields defined in a DebugResource
            return None

        try:
            return self.resource._fields[field]
        except KeyError:
            if not self.ignore_missing_fields:
                raise APIError.BadRequest(
                    "Field '%s' is not expected." % field)

            return None

    def get_resource_from_field(self, field):
        assert isinstance(field, ResourceField)
        return field.resource_type()

    def cast_value(self, field, value):
        if isinstance(field, ResourceListField):
            if not isinstance(value, dict):
                raise APIError.BadRequest(
                    "Expected nested object in list for %s" % field)
            try:
                resource = field.resource_type()
                if isinstance(resource, DebugResource):
                    return value.copy()
                new_object = {}
                for k,v in value.iteritems():
                    if not k in resource._fields and self.ignore_missing_fields:
                        new_object[k] = v
                        continue
                    _field = resource._fields[k]
                    if _field.property_name is not None:
                        k = _field.property_name
                    new_object[k] = self.cast_value(_field, v)

                if not getattr(resource, "_underlying_model", None):
                    return new_object

                return resource._underlying_model(**new_object)
            except Exception:
                logging.exception(
                    "Failed to cast value to _underlying_model of resource_type: %s" %
                    getattr(field, 'resource_type', None))
                raise

        # TODO: Use field to cast field back into a value,
        # if possible.
        return value

    def apply_to_dict(self, dt):
        for k,v in self.patch.iteritems():
            field = self.get_field_from_resource(k)
            if field is None:
                dt[k] = v
                continue
            elif isinstance(v, dict):
                # Recursive application.
                resource = self.get_resource_from_field(field)
                patch = ResourcePatch(v, resource,
                    ignore_missing_fields=self.ignore_missing_fields)
                patch.apply_to_dict(dt[k])
            elif isinstance(v, list):
                if (not isinstance(field, ResourceListField) and
                        not isinstance(field, ListField)):
                    raise APIError.BadRequest(
                        "List not expected for field '%s'" % k)
                new_list = []
                for itm in v:
                    new_list.append(self.cast_value(field, itm))
                dt[k] = new_list
            else:
                # Cast value and store
                dt[k] = self.cast_value(field, v)

    def apply_to_model(self, dt):
        for k,v in self.patch.iteritems():
            field = self.get_field_from_resource(k)
            if field is None:
                setattr(dt, k, v)
            elif isinstance(v, dict):
                # Recursive application.
                resource = self.get_resource_from_field(field)
                patch = ResourcePatch(v, resource,
                    ignore_missing_fields=self.ignore_missing_fields)
                patch.apply_to_model(getattr(dt, k, None))
            elif isinstance(v, list):
                if (not isinstance(field, ResourceListField) and
                        not isinstance(field, ListField)):
                    raise APIError.BadRequest(
                        "List not expected for field '%s'" % k)
                new_list = []
                for itm in v:
                    new_list.append(self.cast_value(field, itm))

                setattr(dt, k, new_list)
            else:
                # Cast value and set
                setattr(dt, k, self.cast_value(field, v))


class PatchEndpoint(Endpoint):
    """Provides a base endpoint for implementing JSON Merge Patch requests.
    See RFC 7386 @ https://tools.ietf.org/html/rfc7386
    """

    MERGE_CONTENT_TYPE = 'application/merge-patch+json'
    _http_method = "PATCH"

    def _handle_patch(self, context, patch):
        raise NotImplementedError("%s should override _handle_patch" %
            self.__class__.__name__)

    def _handle(self, context):
        resource = getattr(self, "_resource", None)
        if not isinstance(resource, Resource):
            raise NotImplementedError(
                "%s needs to define _resource: Resource which will be patched" %
                self.__class__.__name__)

        if (context.headers.get('Content-Type').lower() !=
                self.MERGE_CONTENT_TYPE):
            raise APIError.UnsupportedMedia("PATCH expects content-type %r" %
                self.MERGE_CONTENT_TYPE)

        try:
            patch = ResourcePatch(patch=json.loads(context.body),
                                  resource=resource)
        except Exception, exc:
            raise APIError.UnprocessableEntity(
                "Could not decode JSON from request payload: %s" %
                exc)

        return self._handle_patch(context, patch)


class PutResourceEndpoint(Endpoint):
    """Provides a base endpoint for implementing JSON PUT resource.
    See RFC 7386 @ https://tools.ietf.org/html/rfc7386
    """

    MERGE_CONTENT_TYPE = 'application/json'
    _http_method = "PUT"

    def _handle_put(self, context, patch):
        raise NotImplementedError("%s should override _handle_patch" %
            self.__class__.__name__)

    def _handle(self, context):
        resource = getattr(self, "_resource", None)
        if not isinstance(resource, Resource):
            raise NotImplementedError(
                "%s needs to define _resource: Resource which will be patched" %
                self.__class__.__name__)

        if (context.headers.get('Content-Type').lower() !=
                self.MERGE_CONTENT_TYPE):
            raise APIError.UnsupportedMedia("PATCH expects content-type %r" %
                self.MERGE_CONTENT_TYPE)

        try:
            patch = ResourcePatch(patch=json.loads(context.body),
                                  resource=resource)
        except Exception, exc:
            raise APIError.UnprocessableEntity(
                "Could not decode JSON from request payload: %s" %
                exc)

        return self._handle_put(context, patch)
