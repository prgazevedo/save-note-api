from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

DROPBOX_TOKEN = "sl.u.AFsTgj-qn3n9dCr1_0DTgLkLzjYixma48SrLCXgVhIF0A0tlyOrZj7fKOOuMuzsXwknNrb_5ZCOaTfG6QimJA00FEJB3rFiQduiOSS5ix7GbOkE02ihkocNGacgO7O7lwiS84YlVi9ooaq8gi4Lt7vlqf6cyes5cPHdHtP0vfOWe8eZXi0QiyP-VpQiRCRPbkYoz5JsQYs_dTCMlFlT-kLDAfd1rcYRWsGB7xI4bx3scDXQKRnNsY6RzwFYSvkenQefA9rS_56jkxu__4dMzX5vl2QEonMMp-qaMLYDTi1tQPmH_WtQH_05OVxBkL5_XbiDrlSdMJtosqMu6SdR2kTc7HPTRJUbJ2p8WBFBkdvziZU58TjQ6gkpnhpXBQq813UxMxarff0-zBlbNZEmD1_io9-5X_-Wu2kmgBRk9fFx8y2KXf-O6w-GOFe389bf7kOogGnKdT_-cBXxHm5CkipGE6EZiJOiEDdjvXcyQdNFHtRSC7kYMeSuqOXrVe6fDSbw5KoazN-HFxXDUDyheeaeynpszRxhZR8iteVqTQfSurgfhTWcbITJsM2ZXu8ewELG4CwT4MT3B36Dw04LLxaQvxbAScmX_Vf3EvSKlei2d5mBY-N4GkKmZ2JvdBPoHIisRKIAf2VuXtTdjvOC_oMBnK-tkWk9Fhh7ANJGpbRJp6zOChsDidrE7nbZKo-1PRyJv7RtGdHFTCza8L4waB-laLaHyzW79nNDDof4Eum0T6hsC_shwTchl8O277LsjFwr1qoqRV4i3QO7Cft1j5GgNdDl1hM0wCAD034LHMfmJO1UNCxSfvkt7np0rPi-z4pOWn8wUoJDeh-p-pmmrJM1kATy1-wZGO5_r-p5JgA9L7kCnnWtdAGLlpQSHFUPEEqdny5kHPFWonHqacuGgIN0iQEobqSZ-2K60dgcjg1QPKTjgB0lgERoZ1-aTCprE-GX-BHLYeB3sh-EJmQ-zsIqCrWVqf_UzfxKZfqbN77b-T8CbgnmOfIuRwrhh716uOWGpYxumO9OltT49XX8ZHyhy9YhArIaHH6t6iPpqfPPJAFQAE2I8BagHZElYaIriENTqJzcU7n5mFz8X9f5o2sJQcGcEJbyG_cFtyjhA73xw70aZo5wZmr1hcG1dREuFa_NxY3kVeMAujmCcrZuly0DTkAlsYoKFU0UVNq1lTaTL7VyV3_2IZezndIt52x0St4zNODepXoflOJdhGxYifRrvD__ajnaFnS_5J-8fO_yMzxYrxpg_cGbr7R8jRHZK5v2wccU_tylx-WDCUECpDvjq"

DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"

@app.route("/save_note", methods=["POST"])
def save_note():
    print("📥 Recebida requisição POST em /save_note")

    try:
        data = request.json
        print("🔍 Dados recebidos:")
        print(data)

        title = data.get("title", "untitled").strip().replace(" ", "_")
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        content = data.get("content", "")
        filename = f"{date}_{title}.md"
        dropbox_path = f"/{filename}"

        print(f"📄 Ficheiro a criar: {dropbox_path}")

        headers = {
            "Authorization": f"Bearer {DROPBOX_TOKEN}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({
                "path": dropbox_path,
                "mode": "overwrite",
                "autorename": False,
                "mute": False
            })
        }

        print("📦 Headers enviados:")
        for k, v in headers.items():
            print(f"{k}: {v[:100]}...")

        print("📤 Conteúdo:")
        print(content)

        response = requests.post(
            DROPBOX_UPLOAD_URL,
            headers=headers,
            data=content.encode("utf-8")
        )

        print("📥 Dropbox response:")
        print("Status:", response.status_code)
        print("Body:", response.text)

        if response.status_code == 200:
            return jsonify({"status": "success", "file": filename}), 200
        else:
            return jsonify({
                "status": "error",
                "dropbox_status": response.status_code,
                "dropbox_error": response.text
            }), 500

    except Exception as e:
        print("❌ Exceção:", str(e))
        return jsonify({"status": "error", "exception": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "📝 Save Note API com json.dumps e debug total"

if __name__ == "__main__":
    app.run(debug=True)
