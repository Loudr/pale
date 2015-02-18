Example Pale App
================

This is a simplified pale example app used for testing.

It implements two endpoints:

 * A `GET` endpoint that returns the current time as a JSON object, and
 * A `POST` method that returns a similarly formatted JSON object as the
   other method, but accepts parameters for setting the date.

This is obviously a contrived example, but its purpose is just for testing and
illustrating a little bit of how pale is supposed to be used.


Our experiences with Pale lend themselves to a directory structure similar to
the following:

```
your_web_service/
  api/
    __init__.py
    endpoints/
      __init__.py
      messages/
        __init__.py
        send_message.py
        view_all_conversations.py
        view_conversation.py
      users/
        __init__.py
        create_user.py
        update_profile.py
    resources/
      __init__.py
      conversation.py
      message.py
      user.py
      user_profile.py
  models/
    __init__.py
    database_management.py
    message.py
    user.py
  some_config.yaml
  your_app_entry_point.py
```

Again, this is a bit contrived, but we (the Pale authors) would expect to see
a directory structure similar to this for an API that supports user
registration, profile updating, and sending messages between registered users.

For larger apps, it might make more sense to subdivide by functional units
before splitting up endpoints and resources, which would look like so:

```
your_web_service/
  api/
    __init__.py
    messages/
      __init__.py
      endpoints/
        __init__.py
        send_message.py
        view_all_conversations.py
        view_conversation.py
      resources/
        __init__.py
        conversation.py
        message.py
    users/
      __init__.py
      endpoints/
        __init__.py
        create_user.py
        update_profile.py
      resources/
        __init__.py
        user.py
        user_profile.py
  models/
    __init__.py
    database_management.py
    message.py
    user.py
  some_config.yaml
  your_app_entry_point.py
```

Pale isn't prescriptive in its approach to this, so use what suits you.
