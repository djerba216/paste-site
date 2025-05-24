from flask import Flask, request, redirect, render_template, abort
import uuid
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)

DATA_DIR = "pastes"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_paste_path(paste_id):
    return os.path.join(DATA_DIR, f"{paste_id}.json")

def save_paste(content, expire_minutes=None):
    paste_id = str(uuid.uuid4())[:8]
    expire_time = None
    if expire_minutes:
        expire_time = (datetime.utcnow() + timedelta(minutes=expire_minutes)).isoformat()
    paste = {"content": content, "expire_at": expire_time}
    with open(get_paste_path(paste_id), 'w') as f:
        json.dump(paste, f)
    return paste_id

def load_paste(paste_id):
    path = get_paste_path(paste_id)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        paste = json.load(f)
    if paste["expire_at"]:
        expire_at = datetime.fromisoformat(paste["expire_at"])
        if datetime.utcnow() > expire_at:
            os.remove(path)
            return None
    return paste["content"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form['content']
        expire = request.form.get('expire')
        expire_minutes = int(expire) if expire else None
        paste_id = save_paste(content, expire_minutes)
        return redirect(f"/{paste_id}")
    return render_template('index.html')

@app.route('/<paste_id>')
def view_paste(paste_id):
    content = load_paste(paste_id)
    if content is None:
        abort(404)
    return render_template('view.html', content=content, paste_id=paste_id)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
