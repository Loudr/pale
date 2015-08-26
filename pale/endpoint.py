# -*- coding: utf-8 -*-
import datetime
import json
import logging
import sys

import arrow
from pale import config as pale_config
from pale.arguments import BaseArgument
from pale.errors import APIError, ArgumentError, AuthenticationError
from pale.meta import MetaHasFields
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
                    handle(self._context)

            self._render()
            # After calling ._render(), the response is ready to go, so we
            # shouldn't need to handle any other exceptions beyond this point.
        except AuthenticationError as e:
            if hasattr(e, 'message') and e.message is not None:
                message = e.message
            else:
                message = "You don't have permission to do that."
            err = APIError.Forbidden(message)
            return self._response_class(*err.response)
        except ArgumentError as e:
            err = APIError.UnprocessableEntity(e.message)
            return self._response_class(*err.response)
        except APIError as e:
            return self._response_class(*e.response)
        except PaleRaisedResponse as r:
            return self._response_class(*r.response)
        except Exception as e:
            logging.exception(e)
            raise e

        return self._context.response


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
        json_content = self._json_serializer.encode(rendered_content)
        response_init_list[0] = json_content
        response_init_tuple = tuple(response_init_list)
        if self._response_class is None:
            raise ValueError("""Error with Pale configuration.  Attempted to
            parse a handler result without a response class set on the endpoint.
            This is probably an issue with the pale HTTP adapter you're using,
            since that is where the response class is usually set.""")
        self._context.response = self._response_class(*response_init_tuple)
