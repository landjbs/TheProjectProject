from flask import request, url_for


def url_for_other_page(**kwargs):
    ''' Generates target url with pjax and url_for_args '''
    url_for_args = request.arg.copy()
    if 'pjax' in url_for_args:
        url_for_args.pop('_pjax')
    for k, v in kwargs.items():
        url_for_args[key] = value
    return url_for(request.endpoint, **url_for_args)
