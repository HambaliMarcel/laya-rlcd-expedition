import os
import threading
import time
from pathlib import Path

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000

ROUTES = {
    "task": {
        "instructions": "Decide how this work item should be handled.",
        "criteria": {
            "DO_NOW": "Time-sensitive and high value. Do it yourself before other work.",
            "SCHEDULE": "Worth doing, but not urgent. Put it on the calendar.",
            "DELEGATE": "Someone else should own this. Hand it off.",
            "IGNORE": "Little value, duplicate, or not your responsibility. Drop it.",
        },
    },
    "lead": {
        "instructions": "Decide how to treat this sales lead.",
        "criteria": {
            "PURSUE": "Real need, a buying signal, and a reason to engage now.",
            "NURTURE": "Plausible fit, but timing, budget, or intent is not ready.",
            "LOW_PRIORITY": "Weak fit, no urgency, or unlikely to buy.",
        },
    },
    "proposal": {
        "instructions": "Decide whether to pursue this proposal or tender.",
        "criteria": {
            "PURSUE": "Winnable, worth the effort, and aligned with what you sell.",
            "REVIEW": "Possible, but scope, fit, or odds need a closer look first.",
            "SKIP": "Poor fit, low odds, or the bid cost is not justified.",
        },
    },
    "risk": {
        "instructions": "Rate the delivery, commercial, or relationship risk in this update.",
        "criteria": {
            "LOW": "Unlikely to hurt delivery, cost, or the relationship.",
            "MEDIUM": "A real issue that needs watching and a simple mitigation.",
            "HIGH": "Likely to slip the work, the money, or the relationship if left alone.",
            "CRITICAL": "Immediate threat to delivery, payment, compliance, or the client.",
        },
    },
}

app = Flask(__name__)
router = None
infer_lock = threading.Lock()
status = {
    "state": "loading",
    "detail": "Downloading convaiinnovations/laya on first use.",
}


def load_model():
    global router
    try:
        from laya import Router

        local = Router()
        local.predict(
            "Warmup.",
            {"ready": {"type": "noul", "instructions": "Is this a model warmup?"}},
        )
        router = local
        status["state"] = "loaded"
        status["detail"] = "convaiinnovations/laya"
        print("Laya: Loaded", flush=True)
    except Exception as exc:
        status["state"] = "error"
        status["detail"] = str(exc)
        print("Laya failed to load:", exc, flush=True)


@app.get("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.get("/health")
def health():
    return jsonify(status)


@app.post("/api/decide")
def decide():
    if status["state"] != "loaded" or router is None:
        message = status["detail"] if status["state"] == "error" else "Laya is still loading."
        return jsonify({"error": message}), 503

    body = request.get_json(silent=True) or {}
    text = str(body.get("text") or "").strip()
    kind = body.get("kind")
    route = ROUTES.get(kind)
    if not text:
        return jsonify({"error": "Paste something to analyze."}), 400
    if route is None:
        return jsonify({"error": "Choose a decision type."}), 400
    if len(text) > 20000:
        return jsonify({"error": "That note is too long for one decision. Shorten it and try again."}), 400

    questions = {
        "decision": {
            "type": "choice",
            "instructions": route["instructions"],
            "criteria": route["criteria"],
        }
    }

    try:
        with infer_lock:
            started = time.perf_counter()
            result = router.predict(text, questions)
            latency_ms = (time.perf_counter() - started) * 1000.0
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    answer = (result.get("answers") or {}).get("decision")
    if not answer or answer.get("type") != "choice" or not answer.get("choice"):
        return jsonify({"error": "Laya returned a response this page could not read."}), 502

    routing = result.get("routing") or {}
    return jsonify({
        "decision": answer["choice"],
        "confidence": answer.get("confidence"),
        "probabilities": answer.get("probabilities") or {},
        "model": routing.get("model") or result.get("model") or "laya",
        "repo": routing.get("repo") or "convaiinnovations/laya",
        "latency_ms": round(latency_ms, 1),
    })


if __name__ == "__main__":
    threading.Thread(target=load_model, daemon=True).start()
    print("Work & Sales Router: http://%s:%d" % (HOST, PORT), flush=True)
    app.run(host=HOST, port=PORT, threaded=True)
