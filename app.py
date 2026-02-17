from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'afp_icon_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# The four distinct polls for your session
polls = {
    "1": {
        "question": "Which best describes your current role & shop size?",
        "options": {
            "Solo Fundraiser / I wear all the hats": 0,
            "Frontline Major/Principal Gifts (Large Institution)": 0,
            "Annual Giving / Digital & Mass Philanthropy": 0,
            "Dedicated Donor Relations / Stewardship Team": 0,
            "Advancement Services / Prospect Research / Ops": 0,
            "Advancement Leadership (CDO, VP, ED)": 0,
            "Consultant / Agency / Vendor": 0
        }
    },
    "2": {
        "question": "What is the biggest friction point in your stewardship pipeline?",
        "options": {
            "The Black Hole: Transitioning annual donors to major gift portfolios": 0,
            "Personalization at Scale: Meaningful touchpoints for 150+ assigned prospects": 0,
            "Data Silos: CRM data is too messy for automated stewardship": 0,
            "Writer's Block: Losing hours drafting individual emails and proposals": 0,
            "The Hand-off: Friction between Annual, Major Gifts, and Stewardship teams": 0,
            "Reporting: Churning out high-quality impact reports for endowed funds": 0,
            "Pure Bandwidth: We know what to do, we just lack the staff to do it": 0
        }
    },
    "3": {
        "question": "What is your current reality with generative AI tools?",
        "options": {
            "ChatGPT Plus or Team (OpenAI)": 0,
            "Gemini Advanced / Google Workspace AI": 0,
            "Claude 3 (Anthropic)": 0,
            "Copilot (Microsoft 365)": 0,
            "Fundraising-Specific AI (e.g., Wisely, Gravyty, Windfall)": 0,
            "Shadow IT: I use free web versions secretly because my org blocks it": 0,
            "Still doing everything 100% manually": 0
        }
    },
    "4": {
        "question": "What is the most actionable takeaway you are bringing back to your shop?",
        "options": {
            "Using AI to identify upgrade signals in our existing donor base": 0,
            "Drafting hyper-personalized major gift stewardship cadences with an LLM": 0,
            "Automating the tedious prep work to increase face-to-face donor time": 0,
            "Building an internal policy/framework for safe AI use in our office": 0,
            "Refining my prompting strategy for complex fundraising tasks": 0,
            "Realizing I need to champion AI adoption to my leadership team": 0
        }
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
