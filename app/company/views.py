from flask import request, g, render_template, redirect, url_for

from app.extensions import limiter

from ..company import company


# WARNING: uninitalized init module

@company.route('/company=<code>', methods=['GET', 'POST'])
@limiter.limit('')
def __
