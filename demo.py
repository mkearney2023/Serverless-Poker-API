import requests

try:
    with open('url') as f:
        url = f.read().strip()
except:
    print('url file not found')
    exit()

banner = ('\n'
'┌──────────────────────────────────────────────────────────┐\n'
'│                                                          │\n'
'│  ██╗  ██╗ █████╗ ██╗     ██████╗ ██╗███████╗███╗   ███╗  │\n'
'│  ██║  ██║██╔══██╗██║     ██╔══██╗╚█║██╔════╝████╗ ████║  │\n'
'│  ███████║██║  ██║██║     ██║  ██║ ╚╝█████╗  ██╔████╔██║  │\n'
'│  ██╔══██║██║  ██║██║     ██║  ██║   ██╔══╝  ██║╚██╔╝██║  │\n'
'│  ██║  ██║╚█████╔╝███████╗██████╔╝   ███████╗██║ ╚═╝ ██║  │\n'
'│  ╚═╝  ╚═╝ ╚════╝ ╚══════╝╚═════╝    ╚══════╝╚═╝     ╚═╝  │\n'
'│                                                          │\n'
'└──────────────────────────────────────────────────────────┘\n')

banner_height = len(banner.splitlines())

user_id = ''
lobby_id = ''

def get_table(dicts, keys = [], headers = []):
    if dicts == []: return ''
    if keys == []:
        for dict in dicts:
            for key in dict:
                if key not in keys:
                    keys.append(key)
    if len(headers) != len(keys):
        headers = keys.copy()
    widths = [len(header) for header in headers]
    for i in range(len(keys)):
        for dict in dicts:
            if keys[i] in dict:
                if len(str(dict[keys[i]])) > widths[i]:
                    widths[i] = len(str(dict[keys[i]]))
    output = '\n┌'
    for i in range(len(headers)):
        output += '─' * (widths[i] + 2) + '┬'
    output = output[:-1] + '┐\n'
    for i in range(len(headers)):
        output += '│ ' + headers[i].ljust(widths[i]) + ' '
    output += '│\n├'
    for i in range(len(headers)):
        output += '─' * (widths[i] + 2) + '┼'
    output = output[:-1] + '┤\n'
    for dict in dicts:
        for i in range(len(headers)):
            output += '│ ' + str(dict[keys[i]]).ljust(widths[i]) + ' '
        output += '│\n'
    output += '└'
    for i in range(len(headers)):
        output += '─' * (widths[i] + 2) + '┴'
    output = output[:-1] + '┘\n'
    return output

def display_login():
    global user_id
    while 1:
        actions = {'0': 'register', '1': 'login', '2': 'exit'}
        body = '\n' * 99
        body += banner + '\n'
        for key in actions:
            body += key + '. ' + actions[key] + '\n'
        print(body)
        option = input('')
        response = ''
        if option not in actions:
            input('invalid input\n')
            continue
        elif actions[option] == 'register':
            user_id = input('enter user id: ')
            response = requests.post(url + '/users/' + user_id).text
        elif actions[option] == 'login':
            user_id = input('enter user id: ')
            response = requests.get(url + '/users/' + user_id).text
        elif actions[option] == 'exit':
            break
        if response in ('"user not found"', '"user id taken"'):
            input(response.replace('"', '') + '\n')
            continue
        else:
            display_user()
def display_user():
    global user_id, lobby_id
    while 1:
        user = requests.get(url + '/users/' + user_id).json()
        actions = {'0': 'refresh', '1': 'create lobby', '2': 'join lobby', '3': 'view lobby', '4': 'view debts', '5': 'log out'}
        body = '\n' * 99
        body += banner
        body += get_table(user['lobbies'], ['id'], ['lobbies']) + '\n'
        for key in actions:
            body += key + '. ' + actions[key] + '\n'
        print(body)
        entry = input()
        if entry not in actions:
            input('invalid input\n')
            continue
        elif actions[entry] == 'refresh':
            continue
        elif actions[entry] == 'create lobby':
            lobby_id = input('enter lobby id: ')
            response = requests.post(url + '/users/' + user_id + '/lobbies/' + lobby_id).text
            if response != '"success"':
                input(response.replace('"', '') + '\n')
                continue
        elif actions[entry] == 'join lobby':
            lobby_id = input('enter lobby id: ')
            response = requests.put(url + '/users/' + user_id + '/lobbies/' + lobby_id).text
            if response != '"success"':
                input(response.replace('"', '') + '\n')
                continue
        elif actions[entry] == 'view lobby':
            lobby_id = input('enter lobby id: ')
            if lobby_id not in [l['id'] for l in user['lobbies']]:
                continue
            else:
                display_lobby()
        elif actions[entry] == 'view debts':
            display_debts()
        elif actions[entry] == 'log out':
            break
def display_lobby():
    global user_id, lobby_id
    while 1:
        user = requests.get(url + '/users/' + user_id).json()
        lobby_request = requests.get(url + '/users/' + user_id + '/lobbies/' + lobby_id)
        if lobby_request.text == '"lobby not found"':
            break
        lobby = lobby_request.json()
        lobby['community_cards'] = ' '.join([str(card) for card in lobby['community_cards']])
        for user in lobby['users']:
            user['hole_cards'] = ' '.join([str(card) for card in user['hole_cards']])
            user['hand'] = ' '.join([str(card) for card in user['hand']])
        body = '\n' * 99
        body += banner
        actions = {}
        if lobby['current_round'] == -1:
            body += get_table(lobby['users'], ['id', 'balance', 'vote'], ['user', 'balance', 'vote']) + '\n'
            actions = {'0': 'refresh', '1': 'vote to play', '2': 'vote to exit', '3': 'buy in', '4': 'main menu'}
        elif lobby['current_round'] in (0, 1, 2, 3):
            if lobby['users'][lobby['current_user']]['id'] == user_id:
                body += get_table(lobby['users'], ['id', 'balance', 'bet', 'fold'], ['user', 'balance', 'bet', 'fold']) + '\n'
                if lobby['current_round'] != 0:
                    body += 'community: ' + lobby['community_cards'] + '\n'
                body += 'hole: ' + lobby['users'][next(i for i in range(len(lobby['users'])) if lobby['users'][i]['id'] == user_id)]['hole_cards'] + '\n'
                body += '\n'
                body += 'it is your turn\n'
                body += '\n'
                actions = {'0': 'refresh', '1': 'check/call', '2': 'raise', '3': 'fold', '4': 'main menu'}
            else:
                body += get_table(lobby['users'], ['id', 'balance', 'bet', 'fold'], ['user', 'balance', 'bet', 'fold']) + '\n'
                if lobby['current_round'] != 0:
                    body += 'community: ' + lobby['community_cards'] + '\n'
                body += 'hole: ' + lobby['users'][next(i for i in range(len(lobby['users'])) if lobby['users'][i]['id'] == user_id)]['hole_cards'] + '\n'
                body += '\n'
                body += 'waiting for ' + lobby['users'][lobby['current_user']]['id'] + '\n'
                body += '\n'
                actions = {'0': 'refresh', '1': 'main menu'}
        elif lobby['current_round'] == 4:
            body += get_table(lobby['users'], ['id', 'balance', 'vote', 'hole_cards', 'hand_type', 'hand', 'hand_rank'], ['user', 'balance', 'vote', 'hole', 'result', 'hand', 'rank']) + '\n'
            body += 'community: ' + lobby['community_cards'] + '\n'
            body += 'hole: ' + lobby['users'][next(i for i in range(len(lobby['users'])) if lobby['users'][i]['id'] == user_id)]['hole_cards'] + '\n'
            body += '\n'
            body += next(u['id'] for u in lobby['users'] if u['hand_rank'] == 1) + ' won\n'
            body += '\n'
            actions = {'0': 'refresh', '1': 'vote to play', '2': 'vote to exit', '3': 'buy in', '4': 'main menu'}
        for key in actions:
            body += key + '. ' + actions[key] + '\n'
        print(body)
        entry = input()
        if entry not in actions:
            input('invalid input\n')
            continue
        elif actions[entry] == 'refresh':
            continue
        elif actions[entry] == 'main menu':
            break
        elif actions[entry] == 'vote to play':
            requests.put(url + '/users/' + user_id + '/lobbies/' + lobby_id + '/votes/play')
        elif actions[entry] == 'vote to exit':
            requests.put(url + '/users/' + user_id + '/lobbies/' + lobby_id + '/votes/exit')
        elif actions[entry] == 'buy in':
            amount = input('enter amount: ')
            requests.put(url + '/users/' + user_id + '/lobbies/' + lobby_id + '/actions/buy_in/' + amount)
        elif actions[entry] == 'check/call':
            requests.put(url + '/users/' + user_id + '/lobbies/' + lobby_id + '/actions/call')
        elif actions[entry] == 'raise':
            amount = input('enter amount: ')
            requests.put(url + '/users/' + user_id + '/lobbies/' + lobby_id + '/actions/raise/' + amount)
        elif actions[entry] == 'fold':
            requests.put(url + '/users/' + user_id + '/lobbies/' + lobby_id + '/actions/fold')
def display_debts():
    while 1:
        user = requests.get(url + '/users/' + user_id).json()
        debts = [requests.get(url + '/users/' + user_id + '/debts/' + debt['id']).json() for debt in user['debts']]
        actions = {'0': 'refresh', '1': 'main menu'}
        body = '\n' * 99
        body += banner
        body += get_table(debts, ['time', 'lobby', 'sender', 'receiver', 'amount']) + '\n'
        for key in actions:
            body += key + '. ' + actions[key] + '\n'
        print(body)
        entry = input()
        if entry not in actions:
            input('invalid input\n')
            continue
        elif actions[entry] == 'refresh':
            continue
        elif actions[entry] == 'main menu':
            break

display_login()