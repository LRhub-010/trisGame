from flask import Flask, render_template, session, send_from_directory
import uuid
from tris import register_tris_routes

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'supersecret'

@app.route('/')
def menu():
    if 'player_id' not in session:
        session['player_id'] = str(uuid.uuid4())
    return render_template('menu.html')

# Rotta per il manifest
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

# Rotta per il service worker
@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

# Includi le rotte del gioco Tris
register_tris_routes(app)

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)
