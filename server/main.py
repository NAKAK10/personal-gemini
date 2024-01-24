try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

# noqa
from gemini import GeminiAI
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Flask, request
import time
import os
import threading
import utils
# import markdown


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(50)
socketio = SocketIO(app,
                    cors_allowed_origins=['http://localhost:5173']
                    )


user_instances = {}


def create_user_instance(sid: str):
    user_instances[sid] = {'instance': GeminiAI(), 'last_active': time.time()}


def get_user_instance(sid: str) -> GeminiAI:
    current_time = time.time()
    if sid not in user_instances:
        user_instances[sid] = {'instance': GeminiAI(), 'last_active': current_time}
    else:
        user_instances[sid]['last_active'] = current_time
    return user_instances[sid]['instance']


def remove_inactive_users():
    while True:
        current_time = time.time()
        inactive_users = [sid for sid, data in user_instances.items(
        ) if current_time - data['last_active'] > 300]
        for sid in inactive_users:
            del user_instances[sid]
        time.sleep(60)  # 1分ごとにチェック


# 不活動ユーザー削除スレッドの開始
cleanup_thread = threading.Thread(target=remove_inactive_users, daemon=True)
cleanup_thread.start()


@app.route('/')
def index():
    return 'Hello World'


@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    if sid in user_instances:
        leave_room(sid)
        del user_instances[sid]


@socketio.on('connect')
def on_connect():
    sid = request.sid
    join_room(sid)
    create_user_instance(sid)


@socketio.on('message')
def handle_message(message: dict):
    sid = request.sid
    user_instance = get_user_instance(sid)

    def status_emit(message: str):
        emit('message',
             {
                 'status': 'progress',
                 'role': 'model',
                 'message': message
             },
             broadcast=True,
             room=sid)

    try:
        res = user_instance.get_anything_chat(
            q=message['message'],
            images=message.get('images', []),
            f=status_emit)
        res = res.replace('•', '  *')
        emit('message', {
            'status': 'success',
            'role': 'model',
            'message': res
        }, broadcast=True, room=sid)
    except Exception as e:
        current_time = time.time()
        user_instances[sid] = {'instance': GeminiAI(), 'last_active': current_time}
        utils.red_log(e)

        emit('message', {
            'status': 'error',
            'role': 'model',
            'message': str(e)
        }, broadcast=True, room=sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
