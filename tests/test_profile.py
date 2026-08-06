from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def build_valid_profile_payload() -> dict:
    """Create a reusable valid Page 1 request."""

    return {
        "assessment_id": "ASM-1001",
        "product_name": "Homemade chilli paste",
        "product_category": "processed_condiment",
        "production_scale": "home_kitchen",
        "packaging_type": "glass_bottle",
        "storage_type": "ambient",
        "shelf_life_days": 90,
        "current_certifications": [],
        "other_details": "Produced twice per week",
    }


def test_supported_profile_returns_adaptive_questions() -> None:
    response = client.post(
        "/v1/profile/analyze",
        json=build_valid_profile_payload(),
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["assessment_id"] == "ASM-1001"
    assert response_body["supported"] is True
    assert response_body["unsupported_reason"] is None
    assert response_body["selector_version"] == "rules-v1"
    assert response_body["question_library_version"] == "1.0"

    question_ids = {
        question["id"]
        for question in response_body["selected_questions"]
    }

    assert "Q_HEAT_PROCESS" in question_ids
    assert "Q_SHELF_LIFE_EVIDENCE" in question_ids
    assert "Q_PACKAGING_FOOD_GRADE" in question_ids

    assert len(response_body["selected_questions"]) <= 6


def test_refrigerated_ready_to_eat_product_gets_temperature_question() -> None:
    payload = build_valid_profile_payload()

    payload["product_name"] = "Chicken rice meal"
    payload["product_category"] = "ready_to_eat_meal"
    payload["storage_type"] = "refrigerated"
    payload["packaging_type"] = "plastic_container"
    payload["shelf_life_days"] = 3

    response = client.post(
        "/v1/profile/analyze",
        json=payload,
    )

    assert response.status_code == 200

    question_ids = {
        question["id"]
        for question in response.json()["selected_questions"]
    }

    assert "Q_TEMPERATURE_MONITORING" in question_ids
    assert "Q_FINAL_HANDLING" in question_ids


def test_unsupported_product_returns_no_questions() -> None:
    payload = build_valid_profile_payload()

    payload["product_name"] = "Unclassified food product"
    payload["product_category"] = "other"

    response = client.post(
        "/v1/profile/analyze",
        json=payload,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["supported"] is False
    assert response_body["unsupported_reason"] is not None
    assert response_body["selected_questions"] == []


def test_invalid_shelf_life_is_rejected() -> None:
    payload = build_valid_profile_payload()
    payload["shelf_life_days"] = 0

    response = client.post(
        "/v1/profile/analyze",
        json=payload,
    )

    assert response.status_code == 422