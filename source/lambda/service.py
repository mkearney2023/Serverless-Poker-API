import uuid
import math
import random
import operator
import itertools
import datetime

import dao

user_table = 'poker_users'
lobby_table = 'poker_lobbies'
debt_table = 'poker_debts'

def next_player(lobby):
    if lobby['users'][lobby['current_user']]['fold'] == 1 or lobby['users'][lobby['current_user']]['balance'] == 0:
        num_remaining = len([u for u in lobby['users'] if u['fold'] == 0 and u['balance'] > 0])
        if num_remaining < 2:
            lobby['current_round'] = 4
            end_game(lobby)
    else:
        lobby['current_user'] = (lobby['current_user'] + 1) % len(lobby['users'])
        lobby['current_move'] += 1
        while lobby['users'][lobby['current_user']]['fold'] == 1 or lobby['users'][lobby['current_user']]['balance'] == 0:
            lobby['current_user'] = (lobby['current_user'] + 1) % len(lobby['users'])
            lobby['current_move'] += 1
        if lobby['current_move'] >= len(lobby['users']):
            highest_bet = max([u['bet'] for u in lobby['users']])
            num_remaining = len(list(u for u in lobby['users'] if u['fold'] == 0 and u['bet'] < highest_bet and u['balance'] > 0))
            if num_remaining == 0:
                lobby['current_round'] += 1
                lobby['current_user'] = lobby['first_user']
                lobby['current_move'] = 0
                if lobby['current_round'] == 4:
                    end_game(lobby)
def end_game(lobby):
    lobby['first_user'] = (lobby['first_user'] + 1) % len(lobby['users'])
    lobby['current_user'] = lobby['first_user']
    total_bets = sum(u['bet'] for u in lobby['users'])
    while total_bets > 0:
        highest_bet = max(u['bet'] for u in lobby['users'])
        highest_betters = list(u for u in lobby['users'] if u['bet'] == highest_bet)
        next_highest_bet = 0
        if len(list(u for u in lobby['users'] if u['bet'] != highest_bet)) > 0:
            next_highest_bet = max(u['bet'] for u in lobby['users'] if u['bet'] != highest_bet)
        difference = highest_bet - next_highest_bet
        best_rank = min(u['hand_rank'] for u in highest_betters)
        best_rankers = list(u for u in highest_betters if u['hand_rank'] == best_rank)
        pot = 0
        for u in highest_betters:
            if u['hand_rank'] != best_rank:
                pot += difference
                u['bet'] -= difference
        while pot != 0:
            for u in best_rankers:
                if pot != 0:
                    u['balance'] += 1
                    pot -= 1
        for u in best_rankers:
            u['balance'] += difference
            u['bet'] -= difference
        total_bets = sum(u['bet'] for u in lobby['users'])

def get_user(user_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    if len(user_search) == 0:
        return 'user not found'
    else:
        return user_search[0]
def get_lobby(user_id, lobby_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) == 0:
        return 'lobby not found'
    elif len([u for u in lobby_search[0]['users'] if u['id'] == user_id]) == 0:
        return 'user not in lobby'
    else:
        lobby = lobby_search[0]
        if lobby['current_round'] != 4:
            if lobby['current_round'] == 0:
                lobby['community_cards'] = []
            elif lobby['current_round'] == 1:
                lobby['community_cards'] = lobby['community_cards'][:3]
            elif lobby['current_round'] == 2:
                lobby['community_cards'] = lobby['community_cards'][:4]
            elif lobby['current_round'] == 3:
                lobby['community_cards'] = lobby['community_cards'][:5]
            for u in lobby['users']:
                if u['id'] != user_id:
                    u['hole_cards'] = []
                    u['hand'] = []
                    u['hand_type'] = ''
                    u['hand_rank'] = 0
        return lobby
def get_debt(user_id, debt_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    debt_search = dao.read_items(debt_table, {'id': debt_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(debt_search) == 0:
        return 'debt not found'
    elif user_search[0]['id'] not in (debt_search[0]['sender'], debt_search[0]['receiver']):
        return 'invalid debt'
    else:
        debt = debt_search[0]
        return debt
def create_user(user_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    if len(user_search) > 0:
        return 'user id taken'
    else:
        user = {
            'id': user_id,
            'lobbies': [],
            'debts': [],
            'credits': []
        }
        dao.create_item(user_table, user)
        return 'success'
def create_lobby(user_id, lobby_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) > 0:
        return 'lobby id taken'
    else:
        user = user_search[0]
        user['lobbies'].append({
            'id': lobby_id
        })
        lobby = {
            'id': lobby_id,
            'community_cards': [],
            'first_user': 0,
            'current_user': 0,
            'current_move': 0,
            'current_round': -1,
            'users': [{
                'id': user_id,
                'balance': 0,
                'buy_in': 0,
                'bet': 0,
                'fold': 0,
                'hole_cards': [],
                'hand': [],
                'hand_type': '',
                'hand_rank': 0,
                'vote': ''
            }]
        }
        dao.update_item(user_table, user)
        dao.create_item(lobby_table, lobby)
        return 'success'
def join_lobby(user_id, lobby_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) == 0:
        return 'lobby not found'
    elif len([u for u in lobby_search[0]['users'] if u['id'] == user_id]) > 0:
        return 'user already in lobby'
    else:
        user = user_search[0]
        user['lobbies'].append({
            'id': lobby_id
        })
        lobby = lobby_search[0]
        lobby['users'].append({
            'id': user_id,
            'balance': 0,
            'buy_in': 0,
            'bet': 0,
            'fold': 0,
            'hole_cards': [],
            'hand': [],
            'hand_type': '',
            'hand_rank': 0,
            'vote': ''
        })
        dao.update_item(user_table, user)
        dao.update_item(lobby_table, lobby)
        return 'success'
def vote_play(user_id, lobby_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) == 0:
        return 'lobby not found'
    elif len([u for u in lobby_search[0]['users'] if u['id'] == user_id]) == 0:
        return 'user not in lobby'
    else:
        user = user_search[0]
        lobby = lobby_search[0]
        lobby_user = next((u for u in lobby['users'] if u['id'] == user['id']), None)
        lobby_user['vote'] = 'play'
        votes_play = len([u for u in lobby['users'] if u['vote'] == 'play'])
        if votes_play > len(lobby['users']) - votes_play:
            for u in lobby['users']:
                u['vote'] = ''
            lobby['current_round'] = 0
            num_players = len(lobby['users'])
            deck = [{'value': i, 'rank': math.floor(i / 4), 'suit': i % 4} for i in range(52)]
            random.shuffle(deck)
            community_cards = deck[-5:]
            hole_cards = [deck[i*2:i*2+2] for i in range(num_players)]
            joined_cards = [sorted(community_cards + hole_cards[i], key = operator.itemgetter('value'), reverse = True) for i in range(num_players)]
            card_combinations = [list(map(list, itertools.combinations(joined_cards[i], 5))) for i in range(num_players)]
            hands = []
            scores = []
            types = []
            for card_combination_set in card_combinations:
                best_score = 0
                best_hand = []
                best_type = 0
                for card_combination in card_combination_set:
                    rank_dist = [len([card for card in card_combination if card['rank'] == rank]) for rank in range(13)]
                    group_dist = [len([count for count in rank_dist if count == group]) for group in range(5)][1:]
                    hand_type = 0
                    if group_dist == [5, 0, 0, 0]:
                        is_straight = card_combination[0]['rank'] == card_combination[4]['rank'] + 4
                        is_flush = [card['suit'] for card in card_combination].count(card_combination[0]['suit']) == 5
                        if not is_straight and not is_flush: hand_type = 1
                        elif is_straight and not is_flush: hand_type = 5
                        elif not is_straight and is_flush: hand_type = 6
                        elif is_straight and is_flush: hand_type = 9
                    elif group_dist == [3, 1, 0, 0]: hand_type = 2
                    elif group_dist == [1, 2, 0, 0]: hand_type = 3
                    elif group_dist == [2, 0, 1, 0]: hand_type = 4
                    elif group_dist == [0, 1, 1, 0]: hand_type = 7
                    elif group_dist == [1, 0, 0, 1]: hand_type = 8
                    if hand_type in [2, 3, 4, 7, 8]:
                        is_sorted = False
                        while not is_sorted:
                            is_sorted = True
                            for i in range(len(card_combination) - 1):
                                if card_combination[i]['rank'] != card_combination[i + 1]['rank']:
                                    if rank_dist[card_combination[i]['rank']] < rank_dist[card_combination[i + 1]['rank']]:
                                        card_combination[i], card_combination[i + 1] = card_combination[i + 1], card_combination[i]
                                        is_sorted = False
                    score_values = [str(hand_type)]
                    for card in card_combination:
                        score_values.append(f"{card['rank']:02}")
                    score = int(''.join(score_values))
                    if score > best_score:
                        best_score = score
                        best_hand = card_combination
                        best_type = hand_type
                hands.append(best_hand)
                scores.append(best_score)
                types.append(best_type)
            ranks = [0 for i in range(num_players)]
            current_rank = 1
            while(max(scores) != 0):
                max_score = max(scores)
                while(max(scores) == max_score):
                    ranks[scores.index(max_score)] = current_rank
                    scores[scores.index(max_score)] = 0
                current_rank += 1
            card_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
            card_suits = ['C', 'D', 'H', 'S']
            hand_types = ['', 'high card', 'one pair', 'two pair', 'three of a kind', 'straight', 'flush', 'full house', 'four of a kind', 'straight flush']
            lobby['community_cards'] = [card_ranks[card['rank']] + card_suits[card['suit']] for card in community_cards]
            for i in range(num_players):
                lobby['users'][i]['hole_cards'] = [card_ranks[card['rank']] + card_suits[card['suit']] for card in hole_cards[i]]
                lobby['users'][i]['hand'] = [card_ranks[card['rank']] + card_suits[card['suit']] for card in hands[i]]
                lobby['users'][i]['hand_rank'] = ranks[i]
                lobby['users'][i]['hand_type'] = hand_types[types[i]]
        dao.update_item(lobby_table, lobby)
        return 'success'
def vote_exit(user_id, lobby_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) == 0:
        return 'lobby not found'
    elif len([u for u in lobby_search[0]['users'] if u['id'] == user_id]) == 0:
        return 'user not in lobby'
    else:
        user = user_search[0]
        lobby = lobby_search[0]
        lobby_user = next((u for u in lobby['users'] if u['id'] == user['id']), None)
        lobby_user['vote'] = 'exit'
        votes_exit = len([u for u in lobby['users'] if u['vote'] == 'exit'])
        if votes_exit <= len(lobby['users']) - votes_exit:
            dao.update_item(lobby_table, lobby)
        else:
            for u in lobby['users']:
                u['vote'] = ''
            def get_debt_indices(_lobby):
                num_players = len(_lobby['users'])
                margins = [u['balance'] - u['buy_in'] for u in _lobby['users']]
                all_combos = []
                valid_combos = []
                for i in range(2, math.floor(num_players / 2) + 1):
                    all_combos += list(map(list, itertools.combinations(list(range(num_players)), i)))
                for combo in all_combos:
                    if sum([margins[i] for i in combo]) == 0:
                        complement = [i for i in range(num_players) if combo.count(i) == 0]
                        valid_combo = sorted([combo, complement])
                        if valid_combos.count(valid_combo) == 0:
                            valid_combos.append(valid_combo)
                debts = []
                if len(valid_combos) == 0:
                    resolved = False
                    current_sender = margins.index(min(margins))
                    current_receiver = margins.index(max(margins))
                    while not resolved:
                        if abs(margins[current_sender]) > margins[current_receiver]:
                            debts.append({
                                'sender': current_sender,
                                'receiver': current_receiver,
                                'amount': margins[current_receiver]
                            })
                            margins[current_sender] += margins[current_receiver]
                            margins[current_receiver] = 0
                            current_receiver = margins.index(max(margins))
                        else:
                            debts.append({
                                'sender': current_sender,
                                'receiver': current_receiver,
                                'amount': abs(margins[current_sender])
                            })
                            margins[current_receiver] += margins[current_sender]
                            margins[current_sender] = 0
                            current_sender = margins.index(min(margins))
                        if all(margin == 0 for margin in margins):
                            resolved = True
                else:
                    debts = []
                    debt_count = 999
                    for combo in valid_combos:
                        subset_a = {
                            'users': [{
                                'balance': _lobby['users'][i]['balance'],
                                'buy_in': _lobby['users'][i]['buy_in'],
                            } for i in combo[0]]
                        }
                        subset_b = {
                            'users': [{
                                'balance': _lobby['users'][i]['balance'],
                                'buy_in': _lobby['users'][i]['buy_in'],
                            } for i in combo[1]]
                        }
                        debts_a = get_debt_indices(subset_a)
                        debts_b = get_debt_indices(subset_b)
                        for debt in debts_a:
                            debt['sender'] = combo[0][debt['sender']]
                            debt['receiver'] = combo[0][debt['receiver']]
                        for debt in debts_b:
                            debt['sender'] = combo[1][debt['sender']]
                            debt['receiver'] = combo[1][debt['receiver']]
                        if len(debts_a) + len(debts_b) < debt_count:
                            debts = debts_a + debts_b
                            debt_count = len(debts)
                return debts
            raw_debts = get_debt_indices(lobby)
            debts = []
            time = str(datetime.datetime.now())
            for d in raw_debts:
                debt = {
                    'id': str(uuid.uuid4()),
                    'sender': lobby['users'][d['sender']]['id'],
                    'receiver': lobby['users'][d['receiver']]['id'],
                    'amount': d['amount'],
                    'time': time,
                    'lobby': lobby_id
                }
                debts.append(debt)
                dao.create_item(debt_table, debt)
            users = [dao.read_item(user_table, {'id': u['id']}) for u in lobby['users']]
            for d in debts:
                for u in users:
                    if u['id'] == d['sender']:
                        u['debts'].append({'id': d['id']})
                    elif u['id'] == d['receiver']:
                        u['debts'].append({'id': d['id']})
            for u in users:
                for l in u['lobbies']:
                    if l['id'] == lobby['id']:
                        u['lobbies'].remove(l)
                dao.update_item(user_table, u)
            dao.delete_item(lobby_table, lobby)
        return 'success'
def buy_in(user_id, lobby_id, amount):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) == 0:
        return 'lobby not found'
    elif len([u for u in lobby_search[0]['users'] if u['id'] == user_id]) == 0:
        return 'user not in lobby'
    else:
        user = user_search[0]
        lobby = lobby_search[0]
        user_reference = next((u for u in lobby['users'] if u['id'] == user['id']), None)
        user_reference['buy_in'] += int(amount)
        user_reference['balance'] += int(amount)
        dao.update_item(lobby_table, lobby)
        return 'success'
def call_bet(user_id, lobby_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) == 0:
        return 'lobby not found'
    elif len([u for u in lobby_search[0]['users'] if u['id'] == user_id]) == 0:
        return 'user not in lobby'
    else:
        user = user_search[0]
        lobby = lobby_search[0]
        user_reference = next((u for u in lobby['users'] if u['id'] == user['id']), None)
        user_copy = user_reference.copy()
        highest_bet = max([u['bet'] for u in lobby['users']])
        user_reference['bet'] += min(highest_bet - user_copy['bet'], user_copy['balance'])
        user_reference['balance'] -= min(highest_bet - user_copy['bet'], user_copy['balance'])
        next_player(lobby)
        dao.update_item(lobby_table, lobby)
        return 'success'
def raise_bet(user_id, lobby_id, amount):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) == 0:
        return 'lobby not found'
    elif len([u for u in lobby_search[0]['users'] if u['id'] == user_id]) == 0:
        return 'user not in lobby'
    else:
        user = user_search[0]
        lobby = lobby_search[0]
        user_reference = next((u for u in lobby['users'] if u['id'] == user['id']), None)
        user_copy = user_reference.copy()
        highest_bet = max([u['bet'] for u in lobby['users']])
        user_reference['bet'] += min(highest_bet - user_copy['bet'] + int(amount), user_copy['balance'])
        user_reference['balance'] -= min(highest_bet - user_copy['bet'] + int(amount), user_copy['balance'])
        next_player(lobby)
        dao.update_item(lobby_table, lobby)
        return 'success'
def fold(user_id, lobby_id):
    user_search = dao.read_items(user_table, {'id': user_id})
    lobby_search = dao.read_items(lobby_table, {'id': lobby_id})
    if len(user_search) == 0:
        return 'user not found'
    elif len(lobby_search) == 0:
        return 'lobby not found'
    elif len([u for u in lobby_search[0]['users'] if u['id'] == user_id]) == 0:
        return 'user not in lobby'
    else:
        user = user_search[0]
        lobby = lobby_search[0]
        user_reference = next((u for u in lobby['users'] if u['id'] == user['id']), None)
        user_reference['fold'] = 1
        user_reference['hand_rank'] = 0
        next_player(lobby)
        dao.update_item(lobby_table, lobby)
        return 'success'

