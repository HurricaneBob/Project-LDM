def test_chat_new_session(client):
    r = client.post(
        "/api/chat",
        json={
            "sessionId": None,
            "message": "Let's align on priorities and support the team.",
            "history": [],
        },
    )
    assert r.status_code == 200
    data = r.json
    assert "sessionId" in data
    assert len(data.get("personaResponses", [])) >= 1
    assert "parameterDeltas" in data


def test_chat_continue(client):
    r1 = client.post(
        "/api/chat",
        json={"sessionId": None, "message": "We need clarity under deadline pressure.", "history": []},
    )
    sid = r1.json["sessionId"]
    r2 = client.post(
        "/api/chat",
        json={"sessionId": sid, "message": "I hear you — let's document trade-offs together.", "history": []},
    )
    assert r2.status_code == 200
    assert r2.json["sessionId"] == sid
