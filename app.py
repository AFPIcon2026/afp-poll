from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'afp_icon_secret'
# Allows connections from any device
socketio = SocketIO(app, cors_allowed_origins="*")

# The poll options (customize these for your stewardship session!)
poll_data = {
    "The Welcome Packet": 0,
    "Personal Phone Call": 0,
    "Impact Video": 0,
    "Handwritten Note": 0
}

# The audience view (voting buttons)
@app.route('/')
def audience():
    return render_template('index.html', poll_data=poll_data)

# The presenter view (live chart)
@app.route('/results')
def presenter():
    return render_template('results.html')

# This listens for votes from the audience's phones
@socketio.on('submit_vote')
def handle_vote(data):
    choice = data.get('choice')
    if choice in poll_data:
        poll_data[choice] += 1
        # Instantly broadcast the new totals to the presenter screen
        emit('update_chart', poll_data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)