def test_weather_endpoint_success(client):
    """Verify /api/v1/weather returns real weather and IMD rainfall statistics for a valid district."""
    response = client.get("/api/v1/weather?state=Maharashtra&district=Nagpur")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["state"] == "Maharashtra"
    assert data["district"] == "Nagpur"
    assert "temperature" in data
    assert "humidity" in data
    assert "annual_rainfall" in data
    assert data["annual_rainfall"] > 0
    assert "location_name" in data
    assert "Nagpur" in data["location_name"]


def test_weather_current_alias_endpoint(client):
    """Verify /api/v1/weather/current alias returns valid data."""
    response = client.get("/api/v1/weather/current?state=Punjab&district=Ludhiana")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["state"] == "Punjab"
    assert data["district"] == "Ludhiana"
    assert data["temperature"] > -30.0
    assert data["humidity"] >= 0.0


def test_weather_endpoint_missing_params(client):
    """Verify missing query parameters return 422 Unprocessable Entity."""
    response = client.get("/api/v1/weather")
    assert response.status_code == 422
