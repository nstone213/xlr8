from app import create_app, db
import requests
import config
from flask import g, session, request, render_template, send_from_directory
from app.models import *
from flask_socketio import SocketIO, join_room, emit, leave_room
import secrets
import threading


app = create_app(config.TestingConfig)

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/debug-session')
def debug_session():
    return str(session)

@socketio.on('join')
def handle_join(data):
    room = data['file_id']  # Use file_id as the room identifier
    user_id = data['user_id']
    
    join_room(room)
    emit('user_joined', {'user_id': user_id}, room=room)
    print(f"User {user_id} joined room {room}")


@socketio.on('leave')
def handle_leave(data):
    room = data['file_id']
    user_id = data['user_id']
    
    leave_room(room)
    emit('user_left', {'user_id': user_id}, room=room)
    print(f"User {user_id} left room {room}")

@socketio.on('state_update')
def handle_state_update(data):
    room = data['file_id']
    state = data['state']
    user_id = data['user_id']

    emit('state_update', {'state': state, 'user_id': user_id}, room=room)
    print(f"State updated by {user_id} in room {room}: {state}")




if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    print("Flask app starting...")
    socketio.run(app, host="0.0.0.0", port=5003, debug=True)
