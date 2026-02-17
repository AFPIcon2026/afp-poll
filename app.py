from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'afp_icon_secret')
socketio = SocketIO(app, cors_allowed_origins="*")

# AFP Brand Colors
AFP_NAVY = "#003087"
AFP_GOLD = "#FFCD00"
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap" rel="stylesheet">

# Four sequential polls based on presentation "From First Gift to Forever"
POLLS = [
    {
        "id": 1,
        "question": "Where do most organizations lose new donors?",
        "options": [
            "Day 1 to Day 90 (critical window)",
            "After the first year",
            "During the second gift ask",
            "We don't lose donors—we're great at retention!"
        ]
    },
    {
        "id": 2,
        "question": "What stewardship task do you KNOW works but often skip because it takes too long?",
        "options": [
            "Personalized handwritten notes",
            "Individual impact videos",
            "One-on-one phone calls",
            "Customized welcome packets"
        ]
    },
    {
        "id": 3,
        "question": "How are you currently using AI in your fundraising work?",
        "options": [
            "Drafting donor communications",
            "Researching donor prospects",
            "Analyzing giving patterns",
            "Not using AI yet—here to learn!"
        ]
    },
    {
        "id": 4,
        "question": "What's your first move Monday morning?",
        "options": [
            "Choose 3 high-potential donors to engage",
            "Map their journey phase (welcome/cultivation/invitation)",
            "Use AI to draft strategic touchpoints",
            "All of the above—let's do this!"
        ]
    }
]

# Initialize vote storage for all polls
poll_votes = {poll["id"]: {opt: 0 for opt in poll["options"]} for poll in POLLS}
current_poll_index = 0

@app.route('/')
def audience():
    """Audience voting view - shows current active poll"""
    return render_template('index.html', 
                         poll=POLLS[current_poll_index],
                         poll_number=current_poll_index + 1,
                         total_polls=len(POLLS))

@app.route('/results')
def presenter():
    """Presenter view - live results with controls"""
    return render_template('results.html',
                         polls=POLLS,
                         current_poll=current_poll_index + 1,
                         total_polls=len(POLLS))

@app.route('/api/current-poll')
def get_current_poll():
    """API endpoint to get current poll data"""
    return jsonify({
        'poll': POLLS[current_poll_index],
        'votes': poll_votes[POLLS[current_poll_index]["id"]],
        'poll_number': current_poll_index + 1,
        'total_polls': len(POLLS)
    })

@app.route('/api/all-results')
def get_all_results():
    """API endpoint to get all poll results"""
    return jsonify({
        'polls': POLLS,
        'votes': poll_votes,
        'current_poll': current_poll_index + 1
    })

@socketio.on('submit_vote')
def handle_vote(data):
    """Handle vote submission from audience"""
    global current_poll_index
    choice = data.get('choice')
    poll_id = data.get('poll_id')
    
    # Validate the poll is still active
    if poll_id != POLLS[current_poll_index]["id"]:
        emit('vote_error', {'message': 'This poll is no longer active'})
        return
    
    if choice in poll_votes[poll_id]:
        poll_votes[poll_id][choice] += 1
        # Broadcast updated results to all clients
        emit('update_chart', {
            'poll_id': poll_id,
            'votes': poll_votes[poll_id],
            'total_votes': sum(poll_votes[poll_id].values())
        }, broadcast=True)
        emit('vote_confirmed', {'message': 'Vote recorded!'})

@socketio.on('change_poll')
def handle_change_poll(data):
    """Presenter control to change active poll"""
    global current_poll_index
    action = data.get('action')
    
    if action == 'next' and current_poll_index < len(POLLS) - 1:
        current_poll_index += 1
    elif action == 'prev' and current_poll_index > 0:
        current_poll_index -= 1
    elif action == 'reset':
        # Reset votes for current poll only
        poll_id = POLLS[current_poll_index]["id"]
        poll_votes[poll_id] = {opt: 0 for opt in POLLS[current_poll_index]["options"]}
    elif action == 'reset_all':
        # Reset all votes
        for poll in POLLS:
            poll_votes[poll["id"]] = {opt: 0 for opt in poll["options"]}
        current_poll_index = 0
    
    # Broadcast poll change to all clients
    emit('poll_changed', {
        'poll': POLLS[current_poll_index],
        'votes': poll_votes[POLLS[current_poll_index]["id"]],
        'poll_number': current_poll_index + 1,
        'total_polls': len(POLLS)
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
