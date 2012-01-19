# -*- coding: utf-8 -*-

def get_class(class_string):
    """
    Convert a string version of a function name to the callable object.
    """
    try:
        class_string = class_string.encode('ascii')
        mod_name, class_name = get_mod_func(class_string)
        if class_name != '':
            cls = getattr(__import__(mod_name, {}, {}, ['']), class_name)
            return cls
    except (ImportError, AttributeError):
        pass
    raise ImportError('Failed to import %s' % class_string)


def get_mod_func(class_string):
    """
    Converts 'django.views.news.stories.story_detail' to
    ('django.views.news.stories', 'story_detail')

    Taken from django.core.urlresolvers
    """
    try:
        dot = class_string.rindex('.')
    except ValueError:
        return class_string, ''
    return class_string[:dot], class_string[dot + 1:]