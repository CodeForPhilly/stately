from django.db import models, transaction
from django.utils.text import slugify
from jsonfield import JSONField
from uuid import uuid4


def uniquely_slugify(value, unique_within_qs, uniquify=None, slug_field='slug', **kwargs):
    """
    Create a unique slugified string with respect to a given queryset.

    Arguments:
    ---------
    * unique_within_qs - The queryset to compare the slug against.
    * slug_field - The name of the field to use as the slug field. Default is
        `'slug'`.
    * uniquify - The function used to uniquify the slug if it is already used
        in the queryset. This function takes two arguments: the *initial_slug*
        as a string, and a *counter* that represents the number of iterations
        the uniquifying function has gone through.

    Any other keyword arguments are passed along to the `slugify` function.
    """
    # Initialize count and uniquify
    count = 0
    if uniquify is None:
        uniquify = lambda initial, x: initial + str(x)

    # Create an initial slug
    initial_slug = slug = slugify(value, **kwargs)

    # Check whether the slug is used. Try to uniquify it if it is.
    while unique_within_qs.filter(**{slug_field: slug}).exists():
        count += 1
        slug = uniquify(initial_slug, count)

    return slug


# == Definition Models

class Workflow (models.Model):
    name = models.TextField()
    slug = models.CharField(max_length=64, unique=True)
    context = JSONField(null=True)

    def __str__(self):
        return self.slug

    @property
    def initial_template(self):
        return self.initial_state.template

    @property
    def initial_state(self):
        return self.states.first()

    @property
    def initial_action(self):
        return self.initial_state.actions.first()

    def initialize_case(self, commit=False):
        case = Case(
            workflow=self,
            state=self.initial_state)
        if commit:
            case.save()
        return case

    @classmethod
    def load_from_config_str(cls, configstr):
        import yaml
        config = yaml.loads(configstr)
        return cls.load_from_config(config)

    @classmethod
    def load_from_config_file(cls, configfilename):
        import yaml
        with open(configfilename) as configfile:
            config = yaml.load(configfile)
        return cls.load_from_config(config)

    @classmethod
    @transaction.atomic()
    def load_from_config(cls, config):
        if 'states' not in config:
            raise ValueError('Configuration must define some states.')

        name = config['name']
        context = config.get('context')

        workflow = cls(name=name, context=context)
        workflow.slug = uniquely_slugify(name, Workflow.objects.all())
        workflow.save()

        initial = True
        for statecfg in config['states']:
            State.load_from_config(workflow, statecfg, initial=initial)
            initial=False

        return workflow


class State (models.Model):
    workflow = models.ForeignKey('Workflow', related_name='states')
    name = models.TextField()
    slug = models.CharField(max_length=64)

    class Meta:
        unique_together = [('slug', 'workflow')]

    def __str__(self):
        return ':'.join((self.workflow.slug, self.slug))

    @property
    def template(self):
        return eval(self.template_func)()

    @classmethod
    @transaction.atomic()
    def load_from_config(cls, workflow, config, initial=False):
        if 'name' not in config:
            raise ValueError('No name found in config: {}'.format(config))
        if initial and len(config.get('actions', [])) != 1:
            raise ValueError('Initial state must have exactly one action: {}'.format(config))

        name = config['name']

        state = cls(workflow=workflow, name=name)
        state.slug = uniquely_slugify(name, State.objects.filter(workflow=workflow))
        state.initial = initial
        state.save()

        if 'actions' in config:
            for actioncfg in config['actions']:
                Action.load_from_config(state, actioncfg)

        return state


class Action (models.Model):
    name = models.TextField()
    handler = models.TextField(default='')
    template = models.TextField(default='')
    state = models.ForeignKey('State', related_name='actions')

    def __str__(self):
        return ':'.join((self.state.workflow.slug, self.state.slug, self.name))

    @classmethod
    @transaction.atomic()
    def load_from_config(cls, state, config):
        import json

        if 'name' not in config:
            raise ValueError('No name found in config: {}'.format(config))

        name = config['name']
        handler = config.get('handler', '')
        template = config.get('template', '')

        if not isinstance(template, str):
            template = json.dumps(template)

        action = cls(state=state, name=name, template=template, handler=handler)
        action.save()
        return action


# == Instance Models

class Case (models.Model):
    workflow = models.ForeignKey('Workflow')
    state = models.ForeignKey('State')
    create_dt = models.DateTimeField(auto_now_add=True)
    data = JSONField()

    def get_latest_data(self):
        data = {}
        for event in self.events.all().order_by('timestamp'):
            data.update(event.data)
        return data

    def create_initial_event(self, data):
        return Event.objects.create(
            case=self,
            data=data,
            actor=None,
            action=self.workflow.initial_action,
            end_state=self.state,
        )

    def create_event(self, action, actor, data=None):
        return Event.objects.create(
            case=self,
            data=data,
            actor=actor,
            action=action,
            end_state=self.state,
        )


class Actor (models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64)
    case = models.ForeignKey('Case', related_name='actors')
    state = models.ForeignKey('State')
    actions = models.ManyToManyField('Action')
    expiration_dt = models.DateTimeField(null=True)
    valid = models.BooleanField(default=True)

    def can_access_case(self, case):
        if not self.valid:
            return False
        if case != self.case:
            return False
        return True

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid4()
        return super().save(*args, **kwargs)


class Event (models.Model):
    case = models.ForeignKey('Case', related_name='events')
    actor = models.ForeignKey('Actor', related_name='events', null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.ForeignKey('Action', related_name='events')
    data = JSONField()
    end_state = models.ForeignKey('State')

    def get_handler_context(self):
        class ObjectDict (dict):
            def __getitem__(self, key):
                value = super().__getitem__(key)
                return ObjectDict(value) if isinstance(value, dict) else value

            def __getattr__(self, key):
                return self[key]

            def __setattr__(self, key, value):
                self[key] = value

        context = (self.action.state.workflow.context or {}).copy()
        context['data'] = (self.data or {}).copy()

        # Add in common methods
        context['send_email'] = self._send_email
        context['change_state'] = self._change_state

        return ObjectDict(context)


    def _change_state(self, state):
        self.case.state = self.case.workflow.states.get(name=state)
        self.case.save()

    def _send_email(self, email, state, actions=None):
        from django.core.mail import send_mail

        state = self.case.workflow.states.get(name=state)
        if actions is None:
            actions = state.actions.all()
        else:
            actions = state.actions.filter(name__in=actions)

        actor = Actor.objects.create(
            email=email,
            case=self.case,
            state=state,
        )
        actor.actions=actions

        send_mail(
            'An email from Stately',
            ('This is the body of an email from Stately. '
             'http://localhost:8000/api/{}/{}/?token={}'.format(self.case.workflow.slug, self.case.id, actor.token)),
            'admin@stately.com',
            [email],
        )
