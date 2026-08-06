from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def build_process_payload() -> dict:
    """Create a valid processed-condiment process request."""

    return {
        "assessment_id": "ASM-1001",
        "profile": {
            "product_name": "Homemade chilli paste",
            "product_category": "processed_condiment",
            "production_scale": "home_kitchen",
            "packaging_type": "glass_bottle",
            "storage_type": "ambient",
            "shelf_life_days": 90,
            "current_certifications": [],
            "assessment_tags": [
                "category:processed_condiment",
                "packaging:glass_bottle",
                "scale:home_kitchen",
                "shelf_life:extended",
                "storage:ambient",
            ],
        },
        "process_steps": [
            "Purchase chillies from suppliers",
            "Wash and grind the chillies",
            "Cook the mixture",
            "Fill and seal glass bottles",
            "Store the finished bottles",
        ],
        "additional_details": None,
    }


def test_process_analysis_classifies_common_steps() -> None:
    response = client.post(
        "/v1/process/analyze",
        json=build_process_payload(),
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["assessment_id"] == "ASM-1001"
    assert response_body["analyzer_version"] == "rules-v1"
    assert response_body["rule_library_version"] == "1.0"

    stage_ids = {
        step["stage_id"]
        for step in response_body["normalized_steps"]
    }

    assert "raw_material_receiving" in stage_ids
    assert "washing_and_preparation" in stage_ids
    assert "thermal_processing" in stage_ids
    assert "packaging" in stage_ids

    assert len(response_body["photo_requests"]) <= 5
    assert len(response_body["document_requests"]) <= 2


def test_heat_and_packaging_photos_are_requested() -> None:
    response = client.post(
        "/v1/process/analyze",
        json=build_process_payload(),
    )

    assert response.status_code == 200

    response_body = response.json()

    photo_request_ids = {
        request["id"]
        for request in response_body["photo_requests"]
    }

    assert "PHOTO_HEATING_EQUIPMENT" in photo_request_ids
    assert "PHOTO_PACKAGING_AREA" in photo_request_ids
    assert "PHOTO_WORKSPACE" in photo_request_ids

    document_request_ids = {
        request["id"]
        for request in response_body["document_requests"]
    }

    assert "DOC_PRODUCT_LABEL" in document_request_ids
    assert "DOC_INGREDIENT_LIST" in document_request_ids


def test_refrigerated_product_requests_cold_storage_evidence() -> None:
    payload = build_process_payload()

    payload["assessment_id"] = "ASM-1002"
    payload["profile"]["product_name"] = "Chicken rice meal"
    payload["profile"]["product_category"] = "ready_to_eat_meal"
    payload["profile"]["packaging_type"] = "plastic_container"
    payload["profile"]["storage_type"] = "refrigerated"

    payload["process_steps"] = [
        "Purchase chicken and vegetables",
        "Wash and cut the ingredients",
        "Cook the meal",
        "Pack into plastic containers",
        "Keep in refrigerator before delivery",
    ]

    response = client.post(
        "/v1/process/analyze",
        json=payload,
    )

    assert response.status_code == 200

    response_body = response.json()

    photo_request_ids = {
        request["id"]
        for request in response_body["photo_requests"]
    }

    document_request_ids = {
        request["id"]
        for request in response_body["document_requests"]
    }

    assert "PHOTO_COLD_STORAGE" in photo_request_ids
    assert "DOC_TEMPERATURE_LOG" in document_request_ids


def test_more_than_five_process_steps_is_rejected() -> None:
    payload = build_process_payload()

    payload["process_steps"] = [
        "Purchase ingredients",
        "Wash ingredients",
        "Cut ingredients",
        "Cook product",
        "Pack product",
        "Deliver product",
    ]

    response = client.post(
        "/v1/process/analyze",
        json=payload,
    )

    assert response.status_code == 422


def test_duplicate_process_steps_are_rejected() -> None:
    payload = build_process_payload()

    payload["process_steps"] = [
        "Purchase ingredients",
        "Purchase ingredients",
    ]

    response = client.post(
        "/v1/process/analyze",
        json=payload,
    )

    assert response.status_code == 422


def test_unknown_step_is_marked_unclassified() -> None:
    payload = build_process_payload()

    payload["process_steps"] = [
        "Perform our special production activity",
    ]

    response = client.post(
        "/v1/process/analyze",
        json=payload,
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["unclassified_step_count"] == 1
    assert (
        response_body["normalized_steps"][0]["stage_id"]
        == "unclassified"
    )