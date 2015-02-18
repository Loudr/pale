import json
import logging

from pale import config as pale_config
from pale.errors import APIError, ArgumentError, AuthenticationError
from pale.response import PaleRaisedResponse

class Endpoint(object):

    __response_class = None
    __json_serializer = json.JSONEncoder()
    arguments = None


    def set_response_class(self, response_class):
        """Sets the response class for this endpoint.  This is usually only
        called by the Pale adapter, and intended to be called with the Response
        object of the HTTP layer that you're using."""
        self.__response_class = response_class


    @classmethod
    def set_json_serializer(cls, serializer):
        cls.__json_serializer = serializer


    def handle(self, context):
        """The meat of the API logic.  This method is intended to be overridden
        by subclasses, and should perform the core logic of the API method in
        question.
        """
        pass


    def execute(self, request, **kwargs):
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
            self.create_context(request)
            self.authenticate()

            self.parse_args()

            if hasattr(self, 'before_handlers') and \
                    isinstance(self.before_handlers, (list, tuple)):
                for handler in self.before_handlers:
                    handler(self.context)

            self.context.handler_result = self.handle(self.context)

            if hasattr(self, 'after_handlers') and \
                    isinstance(self.after_handlers, (list, tuple)):
                for handler in self.after_handlers:
                    handle(self.context)

            self.render()
            # After calling .render(), the response is ready to go, so we
            # shouldn't need to handle any other exceptions beyond this point.
        except AuthenticationError as e:
            if hasattr(e, 'message') and e.message is not None:
                message = e.message
            else:
                message = "You don't have permission to do that."
            err = APIError.Forbidden(message)
            return err.response
        except ArgumentError as e:
            err = APIError.UnprocessableEntity(e.message)
            return err.response
        except APIError as e:
            return e.response
        except PaleRaisedResponse as r:
            return r.response
        except Exception as e:
            logging.error(e.message)
            import traceback
            traceback.print_exc()
            raise e

        return self.context.response


    def create_context(self, request):
        if pale_config.create_context is None:
            raise ValueError((
                    "\n\nPale does not appear to be configured, as there is no "
                    "context creator currently set!\n\n"))
        self.context = pale_config.create_context(self, request)


    def authenticate(self):
        if pale_config.authenticate_context is None:
            raise ValueError((
                    "\n\nPale does not appear to be configured, as there is no "
                    "context authenticator currently set!\n\n"))
        pale_config.authenticate_context(self.context)


    def patch_args(self):
        # do something like:
        # version = self.context.api_version
        # coersion_dict = self.grab_version_coersion_info_from_impl(version)
        # self.patched_args = self.coerce(self._raw_args, coersion_dict)

        # but for now, just push the raw args through
        self.context.patched_args = self.context._raw_args


    def parse_args(self):
        self.patch_args()

        parsed_args = {}
        if self.arguments is not None:
            if not isinstance(self.arguments, dict):
                raise ValueError("""Your API implementation is broken.  This
                endpoint's `arguments` value is a `%s` when it should be a dict
                instead.  Please see the Pale documentation for information on
                how to fix the problem.""" % (type(self.arguments), ))

            for arg_name, arg_obj in self.arguments.iteritems():
                passed_in_value = self.context.patched_args.get(arg_name, None)

                # HTTP libraries are crap, so we expect `passed_in_value` to
                # be a list, which we strip out if the length is 1 and if the
                # validator doesn't expect a list
                if passed_in_value is not None and \
                        len(passed_in_value) == 1 and \
                        list not in arg_obj.allowed_types:
                    passed_in_value = passed_in_value[0]

                # validate will return the validated (and thus valid) value on
                # success, or raise an ArgumentError if the value is invalid
                validated_value = arg_obj.validate(passed_in_value, arg_name)
                if validated_value is not None:
                    parsed_args[arg_name] = validated_value
        self.context.args = parsed_args


    def parse_handler_result(self, result):
        """Parses the item(s) returned by your handler implementation, which
        may be a lone dict, or maybe a tuple that gets passed to the Response
        class __init__ method of your HTTP layer.  This method separates the
        content dictionary from the rest of the tuple, and returns (a tuple of)
        the content dictionary, and the either a) a list version of the
        original tuple, if the original return value was indeed a tuple, or b)
        a list containing the content dictionary, if the original return value
        was only the dictionary.
        """
        if isinstance(result, dict):
            content_dict = result
            list_result = [""]
        elif isinstance(result, (list, tuple)):
            content_dict = result[0]
            list_result = list(result)
        else:
            raise ValueError("""Your Pale implementation is broken.  Endpoint
            handlers must return either a dictionary response, or a tuple that
            matches the arguments required by your HTTP implementation's
            Response object.""")

        return content_dict, list_result


    def render(self):
        # first, serialize the Python objects in the response_dict into a dict
        rendered_content = {}

        unrendered_content, response_init_list = self.parse_handler_result(
                self.context.handler_result)

        if hasattr(unrendered_content, 'iteritems'):
            for k, v in unrendered_content.iteritems():
                # usually there should only be one key and value here
                dict_val = self.returns.render_serializable(v, self.context)

                # this is where object versioning should be implemented, but one
                # outstanding question with it is, should this be the responsibility
                # of the Resource object, or of the endpoint?

                # coerced_dict_val = self.returns.versionify(dict_val,
                #        self.context.api_version)

                rendered_content[k] = dict_val
        else:
            # maybe it's a nonetype or a simple string?
            rendered_content = self.returns.render_serializable(
                    unrendered_content, self.context)

        # now build the response
        json_content = self.__json_serializer.encode(rendered_content)
        response_init_list[0] = json_content
        response_init_tuple = tuple(response_init_list)
        if self.__response_class is None:
            raise ValueError("""Error with Pale configuration.  Attempted to
            parse a handler result without a response class set on the endpoint.
            This is probably an issue with the pale HTTP adapter you're using,
            since that is where the response class is usually set.""")
        self.context.response = self.__response_class(*response_init_tuple)
