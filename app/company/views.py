from flask import request, g, render_template, redirect, url_for

from app.extensions import limiter

from .models import Company

from ..company import company


# WARNING: uninitalized init module

@company.route('/company=<code>', methods=['GET', 'POST'])
@limiter.limit('')
def company_page(code):
    company = Company.query.filter_by(code=code).first_or_404()
    return render_template('company.html', company=company)
