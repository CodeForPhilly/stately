from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template

def send_login_email(auth, **email_kwargs):
    recipient_list = email_kwargs.pop('recipient_list', [auth.actor.email])
    from_email = email_kwargs.pop('from_email', settings.DEFAULT_FROM_EMAIL)

    subject = email_kwargs.pop('subject', None)
    message = email_kwargs.pop('message', None)

    if subject is None:
        subject = 'Sign in to Stately'
    if message is None:
        scheme = settings.UI_SCHEME
        host = settings.UI_HOST
        token = auth.token

        message = (
            'Hello from Stately!\n\n'
            'Someone has requested a sign in link to access workflows and '
            'cases in stately. If this sounds familiar, click the link below '
            'or copy it into your browser bar to sign in:\n\n'
            '{scheme}://{host}/verify/?token={token}\n\n'
            'If you did not request to sign in link, please ignore this email.'
        ).format(**locals())

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        **email_kwargs
    )


def send_assignment_email(event, assignment):
    body_template = Template(
        'You have been assigned to {{ workflow.name }} case #{{ case.id }}. '
            '{% if actions|length == 0 %}'
                'Please review the case at the link below:\n\n'
            '{% else %}'
                'You must '
                '{% if actions|length == 1 %}'
                    '{{ actions.0.name }}'
                '{% else %}'
                    '{% for action in actions %}'
                        '{% if not forloop.first %}, {% endif %}'
                        '{% if forloop.last %}or {% endif %}'
                        '{{ action.name }}'
                    '{% endfor %}'
                '{% endif %}'
                ' for the case to proceed. Please follow the link below:\n\n'
            '{% endif %}'
        '{{ settings.UI_SCHEME }}://{{ settings.UI_HOST }}/{{ workflow.slug }}/{{ case.id }}/?token={{ assignment.token }}'
    )
    context = Context({
        'case': event.case,
        'assignment': assignment,
        'actions': assignment.actions.all(),
        'workflow': event.case.workflow,
        'settings': settings,
    })

    subject = '{} Case Assignment'.format(event.case.workflow.name)
    send_mail(
        subject,
        body_template.render(context),
        event.get_assigner_email(),
        [assignment.actor.email],
    )
