def test_crop_recommendation_success(client):
    """Verify /api/v1/crop/recommend returns valid top-k recommendations with real probabilities and suitability."""
    payload = {
        "N": 35.0,
        "P": 70.0,
        "K": 45.0,
        "temperature": 26.0,
        "humidity": 68.0,
        "ph": 6.7,
        "rainfall": 850.0,
        "top_k": 5,
        "state": "Maharashtra",
        "district": "Nagpur"
    }
    response = client.post("/api/v1/crop/recommend", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert "recommended_crop" in data
    assert "confidence" in data
    assert "suitability" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 1
    assert len(data["primary_recommendations"]) >= 1
    assert data["recommendations"][0]["is_primary"] is True
    assert data["recommendations"][0]["crop"] in ["soybean", "cotton", "pigeonpeas", "maize"]
    assert data["recommendations"][0]["model_score"] > 0
    assert data["recommendations"][0]["agronomic_score"] > 0
    assert data["confidence"] > 0.0
    assert data["execution_time_ms"] > 0


def test_crop_recommendation_rice_conditions(client):
    """Verify /api/v1/crop/recommend under high rainfall and waterlogged conditions recommends rice/sugarcane."""
    payload = {
        "N": 80.0,
        "P": 45.0,
        "K": 40.0,
        "temperature": 25.0,
        "humidity": 85.0,
        "ph": 6.3,
        "rainfall": 1800.0,
        "top_k": 5,
        "state": "West Bengal",
        "district": "Kolkata"
    }
    response = client.post("/api/v1/crop/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["recommended_crop"] in ["rice", "sugarcane", "jute", "banana"]
    assert data["suitability"] in ["Highly Suitable", "Suitable"]


def test_crop_recommendation_invalid_inputs(client):
    """Verify invalid soil/climatic inputs are rejected with 422."""
    # Negative Nitrogen
    res1 = client.post("/api/v1/crop/recommend", json={
        "N": -10.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 100.0
    })
    assert res1.status_code == 422
    assert res1.json()["success"] is False

    # Out-of-bounds pH (> 10)
    res2 = client.post("/api/v1/crop/recommend", json={
        "N": 50.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.0,
        "humidity": 80.0,
        "ph": 12.5,
        "rainfall": 100.0
    })
    assert res2.status_code == 422
