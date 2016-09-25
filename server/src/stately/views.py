import json
from django.core import serializers
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from .models import *

JsonSerializer = serializers.get_serializer('json')
json_serializer = JsonSerializer()

def serialize_case(case, actor=None):
    data = {
        'id': case.pk,
        'created': case.created_dt,
        'workflow': case.workflow.slug,
        'data': case.get_latest_data(),
        'state': {
            'name': case.state.name,
            'actions': [],  # TODO: fix this
        },
        'events': [
            {
                'actor': event.actor.email,
                'timestamp': event.timestamp,
                'data': event.data
            }
            for event in case.events.all()
        ],
    }
    return data

def handle_event(event):
    action = event.action
    context = action.state.workflow.context.copy()
    context['data'] = event.data.copy()
    exec(action.handler, context)

def get_workflow_or_create_case(request, workflow_slug):
    """
    GET,POST /api/:slug
    """
    if request.method == 'GET':
        return get_workflow(request, workflow_slug)
    elif request.method == 'POST':
        return create_case(request, workflow_slug)
    
def get_workflow(request, slug):
    """
    GET /api/:slug
    """
    workflow = get_object_or_404(Workflow, slug=slug)
    case = workflow.initialize_case()
    data = serialize_case(case)
    return JsonResponse(data)
    
def create_case(request, workflow_slug):
    """
    POST /api/:workflow_slug
    """
    workflow = get_object_or_404(Workflow, slug=workflow_slug)
    case = workflow.initialize_case()
    
    data = json.load(request)
    event = case.create_initial_event(data)
    handle_event(event)
    
    response_data = serialize_case(event.case)
    return JsonResponse(response_data)

def get_case(request, workflow_slug, case_id):
    """
    GET /api/:workflow_slug/:case_id
    """
    token = request.GET.get('token')
    try:
        actor = Actor.objects.get(token=token, valid=True)
    except Actor.DoesNotExist:
        return JsonResponse({'error': 'Your actor token is invalid.'}, status_code=403)

    case = get_object_or_404(Case, workflow__slug=workflow_slug, pk=case_id)
    
    if not actor.can_access_case(case):
        return JsonResponse({'error': 'You do not have access to this case.'}, status_code=403)
    
    data = serialize_case(case, actor)
    return JsonResponse(data)
    
def create_event(request, workflow_slug, case_id, action_slug):
    """
    POST /api/:workflow_slug/:case_id/:action_slug
    """
    token = request.GET.get('token')
    try:
        actor = Actor.objects.get(token=token, valid=True)
    except Actor.DoesNotExist:
        return JsonResponse({'error': 'Your actor token is invalid.'}, status_code=403)

    case = get_object_or_404(Case, workflow__slug=workflow_slug, pk=case_id)
    action = get_object_or_404(Case.state.actions, slug=action_slug)

    if not actor.can_take_action(action):
        return JsonResponse({'error': 'You do not have permission to take this action.'}, status_code=403)

    response_data = serialize_case(event.case, actor)
    return JsonResponse(response_data)
