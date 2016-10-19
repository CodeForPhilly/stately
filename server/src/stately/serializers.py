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
    } if actor else None
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
        'assignment': {
            'token': assignment.token,
        } if assignment else None,
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

