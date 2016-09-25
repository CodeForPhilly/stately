from django.db import models, transaction
from django.utils.text import slugify
from jsonfield import JSONField


def uniquely_slugify(value, unique_within_qs, allow_unicode=False, uniquify=None):
    initial_slug = slug = slugify(value)
    count = 0
    if uniquify is None:
        uniquify = lambda initial, x: initial + str(x)
        
    while unique_within_qs.filter(slug=slug).exists():
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

    def initialize_case(self):
        return Case(
            workflow=self,
            state=self.initial_state)
    
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


class Actor (models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64)
    case = models.ForeignKey('Case')
    expiration_dt = models.DateTimeField()
    valid = models.BooleanField(default=True)
    
    def can_access_case(self, case):
        if not valid:
            return False
        
        if case != self.case:
            return False
        
        return True


class Event (models.Model):
    case = models.ForeignKey('Case')
    actor = models.ForeignKey('Actor')
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.ForeignKey('Action')
    data = JSONField()
    end_state = models.ForeignKey('State')
