import json
from django.core import serializers
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from .emails import send_login_email
from .forms import SendAuthTokenForm
from .models import *
from .serializers import serialize_case, serialize_actor

JsonSerializer = serializers.get_serializer('json')
json_serializer = JsonSerializer()

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

def requires_auth_token(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        request.auth = try_get_authenticator(request)
        return view_func(request, *args, **kwargs)
    return wrapper

def try_get_authenticator(request):
    if 'token' in request.GET:
        token = request.GET['token']
    elif 'auth_token' in request.session:
        token = request.session.get('auth_token')
    else:
        raise ViewError('No actor token specified.', status=401)

    try:
        auth = ActorAuthenticator.objects.get(token=token, is_valid=True)
    except ActorAuthenticator.DoesNotExist:
        raise ViewError('Invalid actor token.', status=403)

    set_session_auth(request.session, auth)
    return auth

def try_event_handler(assignment, event):
    try:
        event.run_handler()
        assignment.complete()
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

def get_session_auth(session):
    auth_token = session.get('auth_token')
    if auth_token is not None:
        # If there is an auth_token in the session, try to get the actor from
        # that token.
        try:
            return ActorAuthenticator.objects.select_related('actor').get(token=auth_token)
        except ActorAuthenticator.DoesNotExist:
            return None

def set_session_auth(session, auth):
    session['auth_token'] = auth.token if auth else None
    return auth

def get_or_set_session_auth(session):
    auth = get_session_auth(session)
    created = False
    if not auth:
        actor = Actor.objects.create(email=None)
        auth = ActorAuthenticator(actor=actor)
        set_session_auth(session, auth)
        created = True
    return auth, created


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

    # Pull the actor off of the session and create an assignment for the case's
    # initial action.
    auth, _ = get_or_set_session_auth(request.session)
    actor = auth.actor
    assignment = case.create_initial_assignment(actor)

    # Get the data from the request; create an initial event with the data and
    # run the event handler.
    data = json.loads(request.body.decode())
    event = case.create_initial_event(actor, data)
    try_event_handler(assignment, event)

    # Return the latest state of the case relative to an anonymous actor.
    response_data = serialize_case(case, assignment)
    return JsonResponse(response_data)

@handle_view_errors
@requires_auth_token
def get_case(request, workflow_slug, case_id):
    """
    GET /api/:workflow_slug/:case_id
    """
    # Get the assignment and case; verify that the assignment affords access to
    # the case.
    case = get_object_or_404(Case, workflow__slug=workflow_slug, pk=case_id)

    actor = request.auth.actor
    assignment = actor.get_latest_assignment_for(case)
    if assignment is None:
        raise ViewError('You do not have access to this case.', status=403)

    # Return the latest state of the case relative to this assignment (TODO:
    # should this be relative to the actor?)
    data = serialize_case(case, assignment)
    return JsonResponse(data)

@csrf_exempt
@handle_view_errors
@requires_auth_token
def create_event(request, workflow_slug, case_id, action_slug):
    """
    POST /api/:workflow_slug/:case_id/:action_slug
    """
    # Get the assignment, case, and action; verify that the assignment affords
    # the action on the case.
    case = get_object_or_404(Case, workflow__slug=workflow_slug, pk=case_id)
    action = get_object_or_404(case.current_state.actions, slug=action_slug)
    assignment = request.auth.actor.get_latest_assignment_for(case, with_assignments=True)
    if action not in assignment.actions.all():
        raise ViewError('You are not assigned to take this action on this case.', status=403)

    # Get the data from the request; create an event with the data and run the
    # event handler.
    data = json.loads(request.body.decode())
    event = case.create_event(assignment.actor, action, data)
    try_event_handler(assignment, event)

    # Return the latest state of the case relative to this assignment (TODO:
    # should this be relative to the actor?)
    response_data = serialize_case(case, assignment)
    return JsonResponse(response_data)

@csrf_exempt
@handle_view_errors
def send_auth_token(request):
    """
    POST /api/send-auth-token
    """
    data = json.loads(request.body.decode())

    form = SendAuthTokenForm(data)
    if not form.is_valid():
        raise ViewError('Request is invalid.', status=400, details=form.errors)

    actor, _ = Actor.objects.get_or_create(email=form.cleaned_data['email'])
    auth = ActorAuthenticator.objects.create(actor=actor)
    send_login_email(auth)
    return HttpResponse(status=204)

@csrf_exempt
@handle_view_errors
@requires_auth_token
def authenticate(request):
    """
    POST /api/authenticate
    """
    assert request.auth and request.session.get('auth_token') == request.auth.token
    response_data = serialize_actor(request.auth.actor)
    return JsonResponse(response_data)

@csrf_exempt
def get_or_forget_current_actor(request):
    """
    GET,DELETE /api/actor
    """
    if request.method == 'GET':
        return get_current_actor(request)
    elif request.method == 'DELETE':
        return forget_current_actor(request)

@handle_view_errors
def get_current_actor(request):
    """
    GET /api/actor
    """
    auth = get_session_auth(request.session)
    response_data = serialize_actor(auth.actor if auth else None)
    return JsonResponse(response_data, safe=False if response_data is None else True)

@csrf_exempt
def forget_current_actor(request):
    """
    DELETE /api/actor
    """
    set_session_actor(request.session, None)
    assert request.session.get('auth_token') is None
    response_data = serialize_actor(None)
    return HttpResponse(status=204)

@handle_view_errors
@requires_auth_token
def get_cases_awaiting_action(request):
    """
    GET /api/cases/awaiting
    """
    actor = request.auth.actor
    cases = Case.objects.awaiting_action_by(actor)
    response_data = {'cases': [serialize_case(c) for c in cases]}
    return JsonResponse(response_data)

@handle_view_errors
@requires_auth_token
def get_cases_acted_on(request):
    """
    GET /api/cases/acted
    """
    actor = request.auth.actor
    cases = Case.objects.acted_on_by(actor)
    response_data = {'cases': [serialize_case(c) for c in cases]}
    return JsonResponse(response_data)
