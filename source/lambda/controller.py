import service
import json

methods = [
    {
        'type': 'POST',
        'resource': '/users/{user_id}',
        'function': service.create_user
    },
    {
        'type': 'POST',
        'resource': '/users/{user_id}/lobbies/{lobby_id}',
        'function': service.create_lobby
    },
    {
        'type': 'PUT',
        'resource': '/users/{user_id}/lobbies/{lobby_id}',
        'function': service.join_lobby
    },
    {
        'type': 'PUT',
        'resource': '/users/{user_id}/lobbies/{lobby_id}/votes/play',
        'function': service.vote_play
    },
    {
        'type': 'PUT',
        'resource': '/users/{user_id}/lobbies/{lobby_id}/votes/exit',
        'function': service.vote_exit
    },
    {
        'type': 'PUT',
        'resource': '/users/{user_id}/lobbies/{lobby_id}/actions/buy_in/{amount}',
        'function': service.buy_in
    },
    {
        'type': 'PUT',
        'resource': '/users/{user_id}/lobbies/{lobby_id}/actions/call',
        'function': service.call_bet
    },
    {
        'type': 'PUT',
        'resource': '/users/{user_id}/lobbies/{lobby_id}/actions/raise/{amount}',
        'function': service.raise_bet
    },
    {
        'type': 'PUT',
        'resource': '/users/{user_id}/lobbies/{lobby_id}/actions/fold',
        'function': service.fold
    },
    {
        'type': 'GET',
        'resource': '/users/{user_id}',
        'function': service.get_user
    },
    {
        'type': 'GET',
        'resource': '/users/{user_id}/lobbies/{lobby_id}',
        'function': service.get_lobby
    },
    {
        'type': 'GET',
        'resource': '/users/{user_id}/debts/{debt_id}',
        'function': service.get_debt
    }
]

def parse_request(method, path):
    path_split = path.split('/')[1:]
    for m in methods:
        if method != m['type']:
            continue
        resource_split = m['resource'].split('/')[1:]
        if len(path_split) != len(resource_split):
            continue
        if all(path_split[i] == resource_split[i] or (resource_split[i][0] == '{' and resource_split[i][-1] == '}') for i in range(len(path_split))):
            parameters = {resource_split[i].replace('{','').replace('}',''): path_split[i] for i in range(len(path_split)) if resource_split[i][0] == '{' and resource_split[i][-1] == '}'}
            return m['function'](**parameters)
    return 'invalid request'

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(parse_request(event['httpMethod'], event['path']))
    }