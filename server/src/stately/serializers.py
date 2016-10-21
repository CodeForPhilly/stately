import json

def try_json(string):
    """Try decoding a string as JSON"""
    try:
        return json.loads(string)
    except:
        return string

def serialize_actor(actor):
    data = {
        'email': actor.email,
    } if actor and actor.email else None
    return data

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
            'actions': serialize_assignment_actions(assignment, case.current_state, default_actions),
        },
        'events': serialize_case_events(case),
    }
    return data

def serialize_assignment_actions(assignment, state, default_actions=[]):
    if assignment and assignment.is_awaiting:
        actions = assignment.actions.filter(state=state)
    else:
        actions = default_actions
    return [serialize_action(action) for action in actions]

def serialize_action(action):
    return {
        'name': action.name,
        'slug': action.slug,
        'template': try_json(action.template),
    }

def serialize_case_events(case):
    data = [
        serialize_event(event)
        for event in case.events.all()
    ]
    return data

def serialize_event(event):
    data = {
        'action': {
            'name': event.action.name,
            'slug': event.action.slug,
        },
        'actor': event.actor.email if event.actor else None,
        'timestamp': event.timestamp,
        'data': event.data
    }
    return data
