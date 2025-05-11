from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Lê o token diretamente do ficheiro secreto
try:
DROPBOX_TOKEN = "sl.u.AFtpMJVV2oYaOyL73PD6IrHLjAoLDWBwTHrq2ta3arRYDnXl2e__e9xON2m4kghg2hskfaqRATp9AQCjWyel3Q_GpQMo7QQGLlf7iNmaMK6Rn_o_7nvUfAH4b055SD26RkD1PgIPRfaYi2oxFdxtG_-VUZE_hPkouN46kSXExmm8_VJbdxpNJtbhGFm888bdCtOeaS-SEFYeXrOD_ogS-W4zxbwI8Z_9Yq9VNLDZKtkZsiz52-oC3dM211ny0dOgCLJkex70nDPfMf9EIEVLNA3uz_1QSvgzvBtcfyv5xXmqxw2wogodSO01jReNs6Pwa6nW7e8Bw4HLvhAODLVRP--6E12tNJsxYL5iWHiUEOid-EV005jq7DpewC8bEZtf3ig1cLuDSVY99dSJ_pQ4j5mpR7S-tz-u0ivlAsNWmgGW9S_U96jeijGnsuj9wvvDZuvQMRaHXfznG_sgnNMV9d9IIQ5W82DQrxZrULS7DxT7g4hHjOtgcIojyoHT_eTROtvo88rgwlMfMvseqhJz8fcsprf9vqqufBufVHNHohqFOsyx8G30Nef10hRGNp54z84WA9nN8bNJ1C-g_Q7-wV1G7YCJ7T6PD6uQPgt9AX43WLJwN4YBvfV3lfHU5VmfDh-Vc84VwRRCN3r3DbvKNEpSNWt5q6Zde1S-PRAG0jT_izOmhYFV_RbVkYfsjhj7g5TkSXCW7LJkJgwV_OKZBqXKAv4qsWJUZfMPZx-zQemFAT51-Ya6sUHdyXufKtxBTx55_2dgeFnONW1yi0aGSgdWJeJ_O66IoiV133XzPqRCK0LT6Hh1pqAtRUcl_KbMAFziH6DpMopkgArZQ6fsPJnCejtS69HhNRSM3ZGqtz5HYoa5cn4v3p6xhrQ4i0oxYeSCAR2YA2K5mjlhW_gJkqE3NpxbezsALaPwYe5BSHCC425zJoKOubjMGWknZmdq8uF_NEwTKGoKUNvYSHeDjvnf_MqQIRamaJfWOnZi_hak_EAfkmv_co5O7gVcmf2HqA20yjf4J5YR-v3coPTjfCqU32SGGGGmyke3XqoEBlNbngcDMqO85KYSA4aG-h4dBQ6FC0zTogLnA_YhK5bQrZDvM4-5RFh6bDNYtWmLlXSVfl-yJW_f-_28ssQCf5O6L0PMeBjBBWRln4aWswxmcsqKS6T2OxHlkCvxGs8EO2vH-sxMIJFPCY_dD223ct14WVTaW8rPyfUztiS7RRr4W9uIzvpK72AxtmYsao2UrsABrOT6AYFcBB0M-WQQZerr-U1udOTYb_ywMgcCqfmfE5bw"
#    with open("/etc/secrets/dropbox_token.txt", "r") as f:
#        DROPBOX_TOKEN = f.read().strip()
except Exception as e:
    DROPBOX_TOKEN = None
    print(f"❌ Erro ao ler token do secret file: {e}")

DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"

@app.route("/save_note", methods=["POST"])
def save_note():
    if not DROPBOX_TOKEN:
        return jsonify({"status": "error", "message": "Token Dropbox não encontrado"}), 500

    data = request.json

    title = data.get("title", "untitled").strip().replace(" ", "_")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    content = data.get("content", "")

    filename = f"{date}_{title}.md"
    dropbox_path = f"/{filename}"

    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": f"""{{"path": "{dropbox_path}", "mode": "overwrite", "autorename": false, "mute": false}}"""
    }

    try:
        response = requests.post(
            DROPBOX_UPLOAD_URL,
            headers=headers,
            data=content.encode("utf-8")
        )

        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "file": filename
            }), 200
        else:
            return jsonify({
                "status": "error",
                "dropbox_status": response.status_code,
                "dropbox_error": response.text,
                "dropbox_headers": dict(response.headers)
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "exception": str(e)
        }), 500

@app.route("/", methods=["GET"])
def home():
    return "📝 Save Note API with Dropbox (token from secret file) is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
