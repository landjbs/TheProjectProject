''' Custom validators for WTF_Forms '''

import re
from flask import current_app
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)

from app.link.utils import fix_url


class Email_Ext_Validator(object):
    ''' Validator for allowed email extensions '''
    def __init__(self, allowed=['college.harvard.edu']):
        self.allowed = set(allowed)

    def __call__(self, form, field):
        email = str(field.data)
        ending = email.split('@')[-1]
        if not ending in self.allowed:
            raise ValidationError('Currently only Harvard College emails '
                                  'are allowed.')


class Link_Validator(object):
    ''' Validates link using request and fixes if necessary '''
    def __init__(self):
        pass

    def __call__(self, form, field):
        url = field.data
        fixed_url = fix_url(url)
        if not fixed_url:
            raise ValidationError('Invalid URL.')
        else:
            field.data = fixed_url


class Select_Limit_Validator(object):
    def __init__(self, max):
        self.max = max

    def __call__(self, form, field):
        if len(field.data)>self.max:
            raise ValidationError(f'Must select no more than {self.max} options.')


class EDU_Validator(object):
    def __init__(self):
        pass

    def __call__(self, form, field):
        if current_app.config['REQUIRE_EDU']:
            if not field.data.endswith('.edu'):
                raise ValidationError("College email must end with '.edu'.")
        else:
            pass


## DEPRECATED (for now) ##
# class Site_URL_Validator(object):
#     ''' Validator for http or https URLs from site '''
#     def __init__(self, site):
#         self.site = site
#         matcher = (r'(www\.|http://|https://|http://www\.|https://\.)'
#                    f'{site}.com/'
#                    r'.+')
#         self.matcher = re.compile(matcher)
#
#     def __call__(self, form, field):
#         if not re.match(self.matcher, field.data):
#             raise ValidationError(f"Invalid URL for {self.site}.")
