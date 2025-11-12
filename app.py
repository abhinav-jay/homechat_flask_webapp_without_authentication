from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import eventlet

# Enable Eventlet for async SocketIO operation
eventlet.monkey_patch()

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///family.db"

db = SQLAlchemy(app)
socketio = SocketIO(app)


# ---------------- MODELS ----------------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    messages = Message.query.all()
    return render_template("index.html", messages=messages)


# ---------------- SOCKET.IO ----------------
@socketio.on("send_message")
def handle_send_message(data):
    content = data.get("message", "").strip()
    if content:
        # Save message to DB
        msg = Message(content=content)
        db.session.add(msg)
        db.session.commit()

        # Broadcast message to all connected clients
        emit("receive_message", {"message": content}, broadcast=True)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
