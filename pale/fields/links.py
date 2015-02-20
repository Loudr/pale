from pale.fields.base import BaseField

class RelativeLinksField(BaseField):
    """A field that contains relative links to a Resource.

    This field is inherently a list of relative links, but it's special in
    that it accepts a list of methods that get called to generate the links.
    
    Each of these link generation methods should return a tuple with the
    name of the relative link, as well as the url, i.e.

        ('canonical', 'https://github.com/Loudr/pale')

    The resulting field will render as an object of named URLs, like this:

        'rel': {
            'canonical': 'https://github.com/Loudr/pale'
        }
    """
    value_type = "relative links"

    def __init__(self, description, details=None, link_generators=[]):
        self.description = description
        self.details = details
        self.link_generators = link_generators

    def render(self, obj, name):
        links = {}
        for renderer in self.link_generators:
            name, val = renderer(obj)
            links[name] = val
        return links

