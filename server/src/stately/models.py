from django.db import models
from django.utils.text import slugify
from jsonfield import JSONField


# == Definition Models

class Workflow (models.Model):
    name = models.TextField()
    slug = models.CharField(max_length=64, unique=True)
    
    @property
    def initial_template(self):
        return self.initial_state.template
        
    @property
    def initial_state(self):
        if self.initial_state:
            return self.initial_state
        for state in self.states:
            if state.initial:
                self.initial_state = state
                return state
        raise ValueError('Workflow missing initial state')
    
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
    def load_from_config(cls, config):
        if 'states' not in config:
            raise ValueError('Configuration must define some states.')
        
        name = config['name']
        
        workflow = cls(name=name)
        workflow.slug = slugify(name)
        workflow.save()
        
        for statecfg in config['states']:
            State.load_from_config(workflow, statecfg)
        
        return workflow


class State (models.Model):
    workflow = models.ForeignKey('Workflow', related_name='states')
    name = models.TextField()
    slug = models.CharField(max_length=64)
    initial = models.BooleanField(default=False)
    template_func = models.TextField()
    
    class Meta:
        unique_together = [('slug', 'workflow')]
    
    @property
    def template(self):
        return eval(self.template_func)
    
    @classmethod
    def load_from_config(cls, workflow, config, initial=False):
        if 'name' not in config:
            raise ValueError('No name found in config: {}'.format(config))
        if 'template' not in config and 'template_func' not in config:
            raise ValueError('No template or template function found in config: {}'.format(config))
            
        name = config['name']
        template = config.get('template')
        
        if template is not None:
            template_func = 'lambda *a, **k: """' + template + '"""'
        else:
            template_func = config['template_func']
        
        state = cls(workflow=workflow, name=name, template_func=template_func)
        state.slug = slugify(name)
        state.initial = initial
        state.save()
        
        if 'actions' in config:
            for actioncfg in config['actions']:
                Action.load_from_config(state, actioncfg)
        
        return state
            

class Action (models.Model):
    name = models.TextField()
    handler = models.TextField()
    state = models.ForeignKey('State', related_name='actions')
    
    @classmethod
    def load_from_config(cls, state, config):
        name = config['name']
        handler = config['handler']
        
        action = cls(state=state, name=name, handler=handler)
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


class Event (models.Model):
    case = models.ForeignKey('Case')
    actor = models.ForeignKey('Actor')
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.ForeignKey('Action')
    data = JSONField()
    end_state = models.ForeignKey('State')