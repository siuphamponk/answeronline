from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import time
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Lưu trữ câu trả lời và thời gian trong bộ nhớ để đơn giản
contestants_data = {
    "contestant1": {"name": "Contestant 1", "answer": "", "time": ""},
    "contestant2": {"name": "Contestant 2", "answer": "", "time": ""},
    "contestant3": {"name": "Contestant 3", "answer": "", "time": ""},
    "contestant4": {"name": "Contestant 4", "answer": "", "time": ""}
}

timer = {"duration": 0, "start_time": 0}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    sorted_contestants = sorted(contestants_data.items(), key=lambda x: x[1]['time'] if x[1]['time'] else '99:99:99')
    return render_template('admin.html', contestants=contestants_data, timer=timer, sorted_contestants=sorted_contestants)

@app.route('/contestant/<int:id>')
def contestant(id):
    return render_template('contestant.html', id=id, timer=timer)

@app.route('/set_timer', methods=['POST'])
def set_timer():
    duration = int(request.form['duration'])
    timer['duration'] = duration
    timer['start_time'] = time.time()
    socketio.emit('start_timer', {'duration': duration})
    return redirect(url_for('admin'))

@app.route('/unlock_answers', methods=['POST'])
def unlock_answers():
    socketio.emit('unlock_answers')
    return jsonify(success=True)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    id = data['id']
    answer = data['answer']
    current_time = datetime.now().strftime("%H:%M:%S")
    contestant_key = f"contestant{id}"
    contestants_data[contestant_key]['answer'] = answer
    contestants_data[contestant_key]['time'] = current_time
    sorted_contestants = sorted(contestants_data.items(), key=lambda x: x[1]['time'] if x[1]['time'] else '99:99:99')
    socketio.emit('update_admin', {"contestants": contestants_data, "sorted_contestants": sorted_contestants})
    return jsonify(success=True)

@app.route('/reset_data', methods=['POST'])
def reset_data():
    for key in contestants_data:
        contestants_data[key]['answer'] = ""
        contestants_data[key]['time'] = ""
    return redirect(url_for('admin'))

import eventlet
eventlet.monkey_patch()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

