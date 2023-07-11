from flask import Flask, request, jsonify
import json,pytest
app = Flask(__name__)

weather_data = {
    "San Francisco": {"temperature": 14, "weather": "Cloudy"},
    "New York": {"temperature": 20, "weather": "Sunny"},
    "Los Angeles": {"temperature": 24, "weather": "Sunny"},
    "Seattle": {"temperature": 10, "weather": "Rainy"},
    "Austin": {"temperature": 32, "weather": "Hot"},
}

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_get_weather():
    response = app.test_client().get('/weather/New%20York')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['temperature'] == 20
    assert data['weather'] == 'Sunny'

def test_add_weather(client):
    response = client.post(
        '/weather',
        json={'city': 'Chicago', 'temperature': 18, 'weather': 'Cloudy'}
    )
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in data
    assert 'Weather information added' in data['message']
    assert 'Chicago' in weather_data

def test_update_weather(client):
    response = client.put(
        '/weather/Chicago',
        json={'temperature': 20}
    )
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in data
    assert 'Weather information updated' in data['message']
    assert weather_data['Chicago']['temperature'] == 20

def test_delete_weather(client):
    response = client.delete('/weather/Chicago')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in data
    assert 'Weather information deleted' in data['message']
    assert 'Chicago' not in weather_data


def test_get_weather_error(client):
    response = client.get('/weather/UnknownCity')
    data = json.loads(response.data)
    assert response.status_code == 404
    assert 'error' in data
    assert 'Weather information not found' in data['error']

def test_add_weather_error(client):
    response = client.post(
        '/weather',
        json={'city': 'Delhi', 'temperature': 35}
    )
    data = json.loads(response.data)
    assert response.status_code == 400
    assert 'error' in data
    assert 'Missing required fields' in data['error']

def test_update_weather_error(client):
    response = client.put(
        '/weather/UnknownCity',
        json={'temperature': 22}
    )
    data = json.loads(response.data)
    assert response.status_code == 404
    assert 'error' in data
    assert 'Weather Data not found' in data['error']

def test_delete_weather_error(client):
    response = client.delete('/weather/UnknownCity')
    data = json.loads(response.data)
    assert response.status_code == 404
    assert 'error' in data
    assert 'Weather Data not found' in data['error']

@app.route("/")
def main():
    return "Welcome to Home-Page!"

@app.route("/weather/<string:city>")
def get_weather(city):
    if city in weather_data:
        return weather_data[city]
    else:
        return {"error": f"Weather Data of city: {city} not found"}, 404


@app.route("/weather", methods=["POST"])
def add_weather():
    data = request.get_json()
    city = data.get("city")
    temperature = data.get("temperature")
    weather = data.get("weather")
    if not city or not temperature or not weather:
        return jsonify(error="Missing required fields"), 400
    weather_data[city] = {"temperature": temperature, "weather": weather}
    return jsonify(message=f"Weather Data added for {city}")


@app.route("/weather/<string:city>", methods=["PUT"])
def update_weather(city):
    if city not in weather_data:
        return jsonify(error=f"Weather Data not found for city: {city}"), 404
    data = request.get_json()
    temperature = data.get("temperature")
    weather = data.get("weather")
    if temperature:
        weather_data[city]["temperature"] = temperature
    if weather:
        weather_data[city]["weather"] = weather
    return jsonify(message=f"Weather Data updated for {city}")


@app.route("/weather/<string:city>", methods=["DELETE"])
def delete_weather(city):
    if city not in weather_data:
        return jsonify(error=f"Weather Data of city: {city} not found."), 404

    del weather_data[city]
    return jsonify(message=f"Weather Data of {city} Deleted Successfully")


if __name__ == "__main__":
    app.run(debug=True)
