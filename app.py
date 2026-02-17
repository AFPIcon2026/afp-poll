from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'afp_icon_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# The four distinct polls for your session
polls = {
    "1": {
        "question": "Who is in the room?",
        "options": {"Major Gifts / Frontline": 0, "Advancement Leadership": 0, "Annual Giving / Comms": 0, "Prospect Dev / Ops": 0}
    },
    "2": {
        "question": "What is your biggest pain point in donor stewardship?",
        "options": {"Securing the initial meeting": 0, "Meaningful touchpoints at scale": 0, "Internal communication/silos": 0, "CRM / Data accuracy": 0}
    },
    "3": {
        "question": "What is your LLM of choice?",
        "options": {"ChatGPT": 0, "Gemini Advanced": 0, "Claude": 0, "Not using AI yet": 0}
    },
    "4": {
        "question": "What is your biggest takeaway from this session?",
        "options": {"AI Prompting Strategies": 0, "New Stewardship Cadences": 0, "Better Internal Collaboration": 0, "Just happy to be in San Diego": 0}
    }
}

# The audience view now requires a poll number (e.g., /1, /2)
@app.route('/<poll_id>')
def audience(poll_id):
    if poll_id not in polls:
        return "Poll not found", 404
    return render_template('index.html', poll_id=poll_id, poll_data=polls[poll_id])

# The presenter view also requires a poll number (e.g., /results/1)
@app.route('/results/<poll_id>')
def presenter(poll_id):
    if poll_id not in polls:
        return "Poll not found", 404
    return render_template('results.html', poll_id=poll_id, poll_data=polls[poll_id])

@socketio.on('submit_vote')
def handle_vote(data):
    poll_id = data.get('poll_id')
    choice = data.get('choice')
    if poll_id in polls and choice in polls[poll_id]["options"]:
        polls[poll_id]["options"][choice] += 1
        # Broadcast the update only to the specific chart that matches the poll_id
        emit('update_chart', {'poll_id': poll_id, 'data': polls[poll_id]["options"]}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
