def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json["status"] == "ok"


def test_init_and_interact(client):
    r = client.post("/api/scenario/init", json={"scenario_index": 1})
    assert r.status_code == 200
    data = r.json
    assert "session_id" in data
    assert data["opening_narration"]
    assert data["dialogue"]

    sid = data["session_id"]
    r2 = client.post(
        "/api/scenario/interact",
        json={"session_id": sid, "user_message": "I hear your concerns. Let's align on priorities together."},
    )
    assert r2.status_code == 200
    assert "dialogue" in r2.json
    assert "p_stabilize" in r2.json


def test_session_state(client):
    r = client.post("/api/scenario/init", json={"scenario_index": 1})
    sid = r.json["session_id"]
    r2 = client.get(f"/api/session/{sid}/state")
    assert r2.status_code == 200
    assert r2.json["session_id"] == sid


def test_final_evaluation(client):
    r = client.post("/api/scenario/init", json={"scenario_index": 1})
    sid = r.json["session_id"]
    r2 = client.post("/api/evaluation/final", json={"session_id": sid})
    assert r2.status_code == 200
    assert "evaluation" in r2.json
