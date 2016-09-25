from django.core import serializers
from django.http import HttpResponseBadRequest
from .models import *

JsonSerializer = serializers.get_serializer('json')
json_serializer = JsonSerializer()

def get_initial_template(request, slug):
    """Get the template to be rendered at the start of a workflow."""
    workflow = Workflow.objects.get(slug=slug)
    name = workflow.name
    initial_template = workflow.initial_template
    response = {
        name: workflow.name,
        initial_template: workflow.initial_template,
    }
    return json_serializer.serialize(response)
    
def create_case(request):
    workflow_id = request.POST.get('workflow')
    workflow = Workflow.objects.get(pk=workflow_id)
    
    Case.objects.create(workflow=workflow_id)
    
def get_case(request, case):
    case = Case.objects.get(pk=case)
    response = {
        state: case.state,
        data: case.data,
    }
    return json_serializer.serialize('json', response)
    
def create_event(request, case, token):
    # Validate token
    try:
        actor = Actor.objects.get(case=case, token=token)
    except Actor.DoesNotExist:
        raise HttpResponseBadRequest('Not a valid token.')
    data = request.POST.get('data')
    Event.objects.create(case_id=case_id, token=token, data=data)
