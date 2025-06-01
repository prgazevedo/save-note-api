from flask import Flask
from routes.upload import upload_note
from routes.list import list_kb, list_kb_folder
from routes.download import get_kb_note
from routes.process_note import process_note 
app = Flask(__name__)

app.add_url_rule("/save_note", view_func=upload_note, methods=["POST"])
app.add_url_rule("/list_kb", view_func=list_kb, methods=["GET"])
app.add_url_rule("/list_kb_folder", view_func=list_kb_folder, methods=["GET"])
app.add_url_rule("/get_kb_note", view_func=get_kb_note, methods=["GET"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
