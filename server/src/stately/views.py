import json
from django.core import serializers
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
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
            'name': case.current_state.name,
            'actions': [
                {
                    'name': action.name,
                    'slug': action.slug,
                    'template': try_json(action.template),
                }
                for action in (assignment.actions.filter(state=case.current_state) if assignment else default_actions)
            ],
        },
        'events': [
            {
                'action': {
                    'name': event.action.name,
                    'slug': event.action.slug,
                },
                'actor': event.actor.email if event.actor else None,
                'timestamp': event.timestamp,
                'data': event.data
            }
            for event in case.events.all()
        ],
    }
    return data

class ViewError (Exception):
    def __init__(self, message, status=500, error_key='error', details=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.error_key = error_key
        self.details = details

    def json_response(self):
        return JsonResponse({self.error_key: self.message, 'details': self.details}, status=self.status)

def handle_view_errors(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ViewError as e:
            return e.json_response()
    return wrapper

def try_get_assignment(token):
    try:
        return Assignment.objects.get(token=token, valid=True)
    except Assignment.DoesNotExist:
        return ViewError('Invalid actor token.', status=403)

def try_event_handler(event):
    try:
        event.run_handler()
    except Event.HandlerError as e:
        raise ViewError(str(e), error_key='handler_error', status=500, details={
            'actor': e.event.actor.email if e.event.actor else None,
            'action': e.event.action.slug,
            'event_data': e.event.data,
            'case_data': e.event.case.get_latest_data(),
            'state': e.event.case.current_state.name,
            'workflow': e.event.case.workflow.slug,
            'case': e.event.case.id,
        })

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
    # Get the workflow and initialize (but do not save) a new case; return the
    # state of that initial case.
    workflow = get_object_or_404(Workflow, slug=slug)
    case = workflow.initialize_case()
    data = serialize_case(case, default_actions=[case.workflow.initial_action])
    return JsonResponse(data)

@csrf_exempt
@handle_view_errors
def create_case(request, workflow_slug):
    """
    POST /api/:workflow_slug
    """
    # Get the workflow and initialize a new case.
    workflow = get_object_or_404(Workflow, slug=workflow_slug)
    case = workflow.initialize_case(commit=True)

    # Get the data from the request; create an initial event with the data and
    # run the event handler.
    data = json.loads(request.body.decode())
    event = case.create_initial_event(data)
    try_event_handler(event)

    # Return the latest state of the case relative to an anonymous actor.
    response_data = serialize_case(event.case)
    return JsonResponse(response_data)

@handle_view_errors
def get_case(request, workflow_slug, case_id):
    """
    GET /api/:workflow_slug/:case_id
    """
    token = request.GET.get('token')

    # Get the assignment and case; verify that the assignment affords access to
    # the case.
    assignment = try_get_assignment(token)
    case = get_object_or_404(Case, workflow__slug=workflow_slug, pk=case_id)

    if not assignment.can_access_case(case):
        return JsonResponse({'error': 'You do not have access to this case.'}, status=403)

    # Return the latest state of the case relative to this assignment (TODO:
    # should this be relative to the actor?)
    data = serialize_case(case, assignment)
    return JsonResponse(data)

@csrf_exempt
@handle_view_errors
def create_event(request, workflow_slug, case_id, action_slug):
    """
    POST /api/:workflow_slug/:case_id/:action_slug
    """
    token = request.GET.get('token')

    # Get the assignment, case, and action; verify that the assignment affords
    # the action on the case.
    assignment = try_get_assignment(token)
    case = get_object_or_404(Case, workflow__slug=workflow_slug, pk=case_id)
    action = get_object_or_404(case.current_state.actions, slug=action_slug)

    if not assignment.can_take_action(case, action):
        raise ViewError('You are not assigned to take this action on this case.', status=403)

    # Get the data from the request; create an event with the data and run the
    # event handler.
    data = json.loads(request.body.decode())
    event = case.create_event(assignment.actor, action, data)
    try_event_handler(event)

    # Return the latest state of the case relative to this assignment (TODO:
    # should this be relative to the actor?)
    response_data = serialize_case(event.case, assignment)
    return JsonResponse(response_data)
