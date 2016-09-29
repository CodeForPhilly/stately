import json
from django.core import serializers
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import *

JsonSerializer = serializers.get_serializer('json')
json_serializer = JsonSerializer()

def try_json(string):
    """Try decoding a string as JSON"""
    try:
        return json.loads(string)
    except:
        return string

def serialize_case(case, assignment=None, default_actions=[]):
    data = {
        'id': case.pk,
        'created': case.create_dt,
        'workflow': {
            'id': case.workflow.id,
            'slug': case.workflow.slug,
            'name': case.workflow.name,
        },
        'data': case.get_latest_data(),
        'state': {
            'name': case.state.name,
            'actions': [
                {
                    'name': action.name,
                    'template': try_json(action.template),
                }
                for action in (assignment.actions.all() if assignment else default_actions)
            ],
        },
        'events': [
            {
                'actor': event.actor.email if event.actor else None,
                'timestamp': event.timestamp,
                'data': event.data
            }
            for event in case.events.all()
        ],
    }
    return data

@csrf_exempt
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
    data = serialize_case(case, default_actions=[case.workflow.initial_action])
    return JsonResponse(data)

def create_case(request, workflow_slug):
    """
    POST /api/:workflow_slug
    """
    workflow = get_object_or_404(Workflow, slug=workflow_slug)
    case = workflow.initialize_case(commit=True)

    data = json.loads(request.body.decode())
    event = case.create_initial_event(data)

    try:
        event.run_handler()
    except Event.HandlerError as e:
        return JsonResponse({'handler_error': str(e)}, status=500)

    response_data = serialize_case(event.case)
    return JsonResponse(response_data)

def get_case(request, workflow_slug, case_id):
    """
    GET /api/:workflow_slug/:case_id
    """
    token = request.GET.get('token')
    try:
        assignment = Assignment.objects.get(token=token, valid=True)
    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Invalid actor token.'}, status=403)

    case = get_object_or_404(Case, workflow__slug=workflow_slug, pk=case_id)

    if not assignment.can_access_case(case):
        return JsonResponse({'error': 'You do not have access to this case.'}, status=403)

    data = serialize_case(case, assignment)
    return JsonResponse(data)

@csrf_exempt
def create_event(request, workflow_slug, case_id, action_slug):
    """
    POST /api/:workflow_slug/:case_id/:action_slug
    """
    token = request.GET.get('token')
    try:
        assignment = Assignment.objects.get(token=token, valid=True)
    except Assignment.DoesNotExist:
        return JsonResponse({'error': 'Invalid actor token.'}, status=403)

    case = get_object_or_404(Case, workflow__slug=workflow_slug, pk=case_id)
    action = get_object_or_404(Case.state.actions, slug=action_slug)

    if not assignment.can_take_action(action):
        return JsonResponse({'error': 'You do not have permission to take this action.'}, status=403)

    data = json.loads(request.body.decode())
    event = case.create_event(actor, action, data)

    try:
        event.run_handler()
    except Event.HandlerError as e:
        return JsonResponse({'handler_error': str(e)}, status=500)

    response_data = serialize_case(event.case, assignment)
    return JsonResponse(response_data)
