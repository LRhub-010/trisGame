from flask import render_template, session, request, jsonify
import uuid
import html

games = []
chat_messages = {}
player_names = {}

def create_new_game():
    return {
        'id': str(uuid.uuid4()),
        'players': [],
        'board': [''] * 9,
        'turn': 'X',
        'winner': None,
        'ready': False,
        'names': {}
    }

def assign_player():
    for game in games:
        if len(game['players']) < 2:
            return game
    new_game = create_new_game()
    games.append(new_game)
    return new_game

def register_tris_routes(app):
    @app.route('/play')
    def index():
        if 'player_id' not in session:
            session['player_id'] = str(uuid.uuid4())

        game = assign_player()
        if session['player_id'] not in game['players']:
            game['players'].append(session['player_id'])
        if len(game['players']) == 2:
            game['ready'] = True

        player_symbol = 'X' if game['players'][0] == session['player_id'] else 'O'
        return render_template("game.html", game_id=game['id'], player_symbol=player_symbol, player_id=session['player_id'])

    @app.route('/move', methods=['POST'])
    def move():
        data = request.json
        game = next(g for g in games if g['id'] == data['game_id'])
        index = int(data['index'])
        player_id = session['player_id']

        if game['winner'] or game['board'][index] != '':
            return jsonify(success=False)

        player_symbol = 'X' if game['players'][0] == player_id else 'O'
        if game['turn'] != player_symbol:
            return jsonify(success=False)

        game['board'][index] = player_symbol

        win_patterns = [
            [0,1,2], [3,4,5], [6,7,8],
            [0,3,6], [1,4,7], [2,5,8],
            [0,4,8], [2,4,6]
        ]
        for a, b, c in win_patterns:
            if game['board'][a] == game['board'][b] == game['board'][c] != '':
                game['winner'] = game['board'][a]

        if '' not in game['board'] and not game['winner']:
            game['winner'] = 'Draw'

        game['turn'] = 'O' if game['turn'] == 'X' else 'X'
        return jsonify(success=True)

    @app.route('/state/<game_id>')
    def state(game_id):
        game = next(g for g in games if g['id'] == game_id)
        return jsonify(
            board=game['board'],
            turn=game['turn'],
            winner=game['winner'],
            ready=game['ready'],
            names=game.get('names', {})
        )

    @app.route('/chat/<game_id>')
    def chat(game_id):
        return jsonify(messages=chat_messages.get(game_id, []))

    @app.route('/chat/send', methods=['POST'])
    def send():
        data = request.json
        game_id = data['game_id']
        msg = data['message'].strip()
        sender = player_names.get(session['player_id'], session['player_id'][:5])
        if not msg:
            return '', 204

        safe_message = f"{html.escape(sender)}: {html.escape(msg)}"
        chat_messages.setdefault(game_id, []).append(safe_message)
        if len(chat_messages[game_id]) > 100:
            chat_messages[game_id] = chat_messages[game_id][-100:]
        return '', 204

    @app.route('/set_name', methods=['POST'])
    def set_name():
        data = request.json
        name = data.get('name', '').strip()
        if name:
            player_names[session['player_id']] = name[:20]
        return '', 204
