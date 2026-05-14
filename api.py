import requests

DATA_URL = "http://157.10.252.46:5000/app_state"


def fetch_signal():
    try:
        r = requests.get(DATA_URL, timeout=5)
        data = r.json()

        return {
            "signal": data.get("signal", "WAITING"),
            "entry_time": data.get("entry_time", "-"),
            "market": data.get("market", "-"),
            "status": data.get("status", "UNKNOWN"),
            "server_time": data.get("server_time", "-")
        }

    except:
        return {
            "signal": "ERROR",
            "entry_time": "-",
            "market": "-",
            "status": "OFFLINE",
            "server_time": "-"
        }
