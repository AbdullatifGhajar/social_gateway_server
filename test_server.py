import pytest

import server

questions = [{"english": f"question {i}", "german": f"Frage {i}"} for i in range(5)]
questions.append({"english": "question <app_name>", "german": f"Frage <app_name>"})


@pytest.fixture
def client():
    server.app.config["TESTING"] = True
    return server.app.test_client()


def test_send_question(client):
    def request_question(**kwargs):
        args = "&".join(f"{key}={value}" for key, value in kwargs.items())
        return client.get(f"/question?{args}").data.decode()

    server.main(testing=True, injected_questions=questions)

    assert request_question(question_id=3) == "question 3"
    assert request_question(question_id=0, language="english") == "question 0"

    assert request_question(question_id=2, language="german") == "Frage 2"
    assert request_question(question_id=1, language="german") == "Frage 1"

    assert request_question(question_id=5, app_name="Telegram") == "question Telegram"
    assert (
        request_question(question_id=5, app_name="pointcloud", language="german")
        == "Frage pointcloud"
    )


def test_receive_answer(client):
    expected_data = {
        "user_id": "NULL",
        "app_name": "NULL",
        "question": "NULL",
        "answer_text": "NULL",
        "answer_audio_uuid": "NULL",
    }

    def write_answer(row):
        for key, value in expected_data.items():
            assert row[key] == value
        assert row["date"]

    server.main(testing=True, injected_write_answer=write_answer)

    response = client.post("/answer", data=b"{}").data.decode()
    assert response == "Thanks for your answer!"

    expected_data["user_id"] = "b3f"
    response = client.post("/answer", data=b'{"user_id": "b3f"}').data.decode()
    assert response == "Thanks for your answer!"

    expected_data.update(
        {
            "app_name": "pushrequest",
            "question": "You afraid of superintelligence?",
            "answer_text": "Oh yes.",
        }
    )
    response = client.post(
        "/answer",
        data=b"""{"user_id": "b3f",
                             "app_name": "pushrequest",
                             "question": "You afraid of superintelligence?",
                             "answer_text": "Oh yes."}""",
    ).data.decode()
    assert response == "Thanks for your answer!"


def test_receive_audio(client):
    assert client.post("/audio").data.decode() == "UUID is required."
    assert (
        client.post("/audio?uuid=b3f").data.decode()
        == client.post("/audio?uuid=b3f", data=b"").data.decode()
        == "Audio data is required."
    )

    def write_audio(file_name, data):
        assert file_name == "audio/b3f.aac"
        assert data == b"test"

    server.main(testing=True, injected_write_audio=write_audio)
    assert (
        client.post("/audio?uuid=b3f", data=b"test").data.decode()
        == "Thanks for your audio answer!"
    )
