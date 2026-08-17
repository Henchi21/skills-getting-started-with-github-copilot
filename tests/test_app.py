import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mergington_app", root_dir / "src" / "app.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_duplicate_signup_is_rejected():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    first_response = client.post(f"/activities/{activity}/signup?email={email}")
    assert first_response.status_code == 200

    second_response = client.post(f"/activities/{activity}/signup?email={email}")
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"
