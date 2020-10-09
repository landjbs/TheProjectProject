from flask import url_for
from wtforms import (TextField, StringField, BooleanField, SelectField,
                    SelectMultipleField, FloatField, IntegerField,
                    TextAreaField, validators, Field, )
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                InputRequired, ValidationError, NumberRange)
# absolute imports
from app.forms.base import BaseForm
from app.forms.validators import Select_Limit_Validator
from app.link.utils import fix_url
# package imports
from app.project.models import Project
from markupsafe import Markup
# from app.company.models import Company


### javascript validators ###



class Add(BaseForm):
    ''' Fields of Add form that are shared between all types '''
    identifier = 'Add'
    # type
    type = SelectField(
        label='What are you working on?',
        validators=[DataRequired()],
        description=(
            'TheProjectProject supports innovation at all stages, whether '
            "it's connnecting your independent project with resources, helping "
            'your early-stage startup build a team, or packaging the projects '
            'your company needs done into microinternship opportunities. '
            "If you are looking to share something you've already worked on "
            'or to put a team together to build a quick idea, select Project. '
            'If you are working on something longer-term, want to connect with '
            'VC firms, or are building something comprised of multiple sub-projects, '
            'select Company.'
        ),
        choices=[(1, 'Project'), (2, 'Company')],
        render_kw={
            'optional': 'false',
            'datamap': {
                1:  {
                    'key'   :   'A',
                    'icon'  :   'fa fa-circle',
                    'action':   "set_type('Project'); hide_class('company'); show_class('project');"
                },
                2:  {
                    'key'   :   'B',
                    'icon'  :   'fa fa-briefcase',
                    'action':   "set_type('Company'); hide_class('project'); show_class('company');"
                }
            },
            'seconds':  3
        }
    )
    # name
    name = StringField(
        label=Markup("<span class='project_type'></span> Name"),
        validators=[DataRequired(), Length(1, 40)],
        description='Give your idea a name!',
        render_kw={
            'optional':     'false',
            'placeholder':  'TheProjectProject',
            'max':          30,
            'seconds':      5
        }
    )
    # oneliner
    oneliner = StringField(
        label='One Line',
        validators=[DataRequired(), Length(1, 100)],
        description=Markup(
            'One line description of your <span class="project_type lowercase"></span>. '
            'No need to overthink this: the One Line should be punchy and succinct.'
        ),
        render_kw={
            'optional':     False,
            'placeholder':'The platform for sharing, collaborating on, and publicizing independent projects.',
            'max': 40,
            'seconds':  20
        }
    )
    # summary
    summary = TextAreaField(
        label='Summary',
        validators=[DataRequired(), Length(1, 400)],
        description=Markup(
            'Describe your <span class="project_type lowercase"></span> in more detail. '
            'If you had 60 seconds to tell your friend about this idea, what would you say?'
        ),
        render_kw={
            'optional':     'false',
            'placeholder': (
                'TheProjectProject is a virtual community of innovators, who collaborate on projects across a wide range of fields and time windows. '
                'I need a team of web developers, database experts, and creative minds to help me build this platform. We will tackle interesting problems '
                'such as matching users with projects they will like and designing an interface that helps people communicate their ideas...'
            ),
            'max':400,
            'seconds':  90
        }
    )
    # subjects
    subjects = SelectMultipleField(
        label='Subjects',
        description=Markup(
            'What subjects might this <span class="project_type lowercase"></span> involve? '
            "If you're interested, we can connect you to people with the skillset you're looking for."
        ),
        validators=[],
        choices=[],
        coerce=int,
        render_kw={
            'seconds':  8
        }
    )
    ### COMPANY ###
    # has_raised
    has_raised = BooleanField(
        label='Have you raised any funding so far?',
        description=(
            "This question helps us better understand your progress and needs "
            'as a company. If you have won any grants or raised any funding, '
            'please let us know.'
        ),
        render_kw={
            'seconds':  5,
            'tabclass': 'company',
            'datamap': {
                'true': {
                    'action':   "show_class('has_raised');"
                },
                'false': {
                    'action':   "hide_class('has_raised');"
                }
            }
        }
    )
    # amount_raised
    amount_raised = IntegerField(
        label='Roughly how much have you raised?',
        validators=[],
        description=(
            "This helps us understand the scale of your company and "
            "(if you're interested) connect you with appropriate "
            'funding opportunities. We will never share this number without '
            'your consent. It does not need to be extremely accurate—just estimate '
            'how much you have raised from VCs, grants, competitions, etc.'
        ),
        render_kw={
            'min':      100,
            'start':    5000,
            'max':      1000000, # current max 1 mil
            'units':    'dollars',
            'step':     100,
            'optional': True,
            'seconds':  5,
            'tabclass': 'company has_raised'
        }
    )
    # looking for funding
    looking_for_funding = BooleanField(
        label='Are you currently looking for funding?',
        validators=[],
        description=(
            'Funding and mentorship are crucial to early-stage companies, '
            "yet these opportunities are hard to come by in the wild. "
            "We are here to help. Select Yes if you'd like to be connected with "
            'funding opportunities.'
        ),
        render_kw={
            'tabclass': 'company',
            'datamap': {
                'true': {
                    'action':   ''
                },
                'false': {
                    'action':   ''
                }
            }
        }
    )
    ### PROJECT ###
    complete = BooleanField(
        label='Have you already completed this project?',
        validators=[],
        description=(
            "TheProjectProject is a great place to show off work you've already "
            "done. Whether it's a final project for a class, an independent project "
            'you built over the summer, or work you did for an internshp, add it '
            "to show off your skills to the world. If this is an idea you want to work on "
            'or are building right now, select No.'
        ),
        render_kw={
            'seconds':  5,
            'tabclass': 'project',
            'datamap': {
                'true':  {
                    'action':   "hide_class('incomplete'); hide_class('looking_for_team'); show_class('complete');"
                },
                'false':  {
                    'action':   "hide_class('complete'); show_class('incomplete'); show_class('looking_for_team');"
                }
            }
        }
    )
    ### COMPLETED PROJECT ###
    time_it_took = IntegerField(
        label='Roughly how many days did it take?',
        validators=[],
        description=(
            'No need to be too accurate, just a rough estimate of how long this '
            'project took to help us better understand the scope.'
        ),
        render_kw={
            'min':      1,
            'start':    30,
            'max':      360,
            'units':     'days',
            'seconds':  5,
            'tabclass': 'project complete'
        }
    )
    ### INCOMPLETE PROJECT ###
    estimated_time = IntegerField(
        label='Roughly how many days do you expect it to take?',
        validators=[],
        description=(
            'TheProjectProject is all about short, impactful projects.'
            'You will be able to extend this time later, if you wish.'
        ),
        render_kw={
            'min':      1,
            'start':    7,
            'max':      60,
            'units':    'days',
            'tabclass': 'project incomplete'
        }
    )
    ### SHARED TEAM BUILDING ###
    working_with_others = BooleanField(
        label='Have you been working with anyone else?',
        description=(
            "Is there anyone else with whom you have been/will be building this?"
        ),
        validators=[],
        render_kw={
            'tabclass': '',
            'datamap': {
                'true': {
                    'action':   "show_class('other_members');"
                },
                'false': {
                    'action':   "hide_class('other_members');"
                }
            }
        }
    )
    # other_members = SelectMultipleField(
    #     label='Please write the email addresses of your teammates.',
    #     description=Markup(
    #         'If they are already members of TheProjectProject, we will add them '
    #         "to your team. If they aren't we will reach out to them, and help "
    #         'them get setup on the site.'
    #     ),
    #     validators=[],
    #     render_kw={
    #
    #     }
    # )
    # TODO: add querying for others
    # others =
    ### INCOMPLETE PROJECT AND COMPANY TEAM BUILDING ###
    looking_for_team = BooleanField(
        label='Are you looking for new team members?',
        description=(
            'TheProjectProject community boasts a diversity of skillsets and '
            'perspectives. Let us know if you might be interested in working '
            'with others and we will connect you with passionate new team-members.'
        ),
        validators=[],
        render_kw={
            'tabclass': 'incomplete',
            'datamap': {
                'true': {
                    'action':   "show_class('looking_for_team');"
                },
                'false': {
                    'action':   "hide_class('looking_for_team')"
                }
            }
        }
    )
    target_team_size = IntegerField(
        label='Roughly how many team members are you looking for?',
        description=(
            'This lets prospective members understand the scope of your project '
            'and helps us match you with new team members. You will be able '
            'to change this number at any point.'
            ),
        validators=[],
        render_kw={
            'min':      1,
            'start':    7,
            'max':      20,
            'units':    'people',
            'tabclass': 'looking_for_team'
        }
    )
    requires_application = BooleanField(
        label='Would you like to create an application to join your project?',
        description=(
            'Applications allow you to ask questions of those seeking to '
            "join your team. We recommended creating one: they're quick and allow "
            'you to control who joins your project.'
        ),
        validators=[],
        render_kw={
            'tabclass': 'project looking_for_team',
            'datamap': {
                'true': {
                    'action':   "show_class('application')"
                },
                'false': {
                    'action':   'hide_class("application")'
                }
            }
        }
    )
    application_question = StringField(
        label=Markup('Ask applicants to your <span class="project_type lowercase"></span> a question.'),
        description=Markup(
            'Members who want to join your <span class="project_type lowercase"></span> '
            'will have to answer this question. You will be able to see what '
            'they say when evaluating their application.'
        ),
        validators=[Length(0, 128)],
        render_kw={
            'placeholder':  '',
            'max': 128,
            'tabclass': 'looking_for_team application'
        }
    )
    ### SHARED COMPETITION ###
    competition = SelectField(
        label=Markup('We found some competitions that might be a good fit for your <span class="project_type lowercase"></span>!'),
        description=Markup(
            'If any of these interest you, select them from the list below '
            'and your <span class="project_type lowercase"></span> will '
            'automatically be submitted.'
        ),
        validators=[],
        choices=[],
        render_kw={
            'optional':     'true',
            'searchable':   True,
            'tabclass':     ''
        }
    )

    def total_time(self):
        time = 0
        for field in self:
            try:
                time += field.render_kw['seconds']
            except:
                print(f'WARNING: {field.name} has no render_kw')
        return time
