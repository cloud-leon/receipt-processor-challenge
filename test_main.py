import os
import json
import requests

EXAMPLES_DIR = "examples"
import pytest
import requests
import json

BASE_URL = "http://localhost:8000"


def test_process_receipt():
    # Load example receipt
    with open("examples/morning-receipt.json", "r") as file:
        example_receipt = json.load(file)

    # Submit the receipt
    response = requests.post(f"{BASE_URL}/receipts/process", json=example_receipt)
    assert response.status_code == 200
    assert "id" in response.json()


def test_get_points():
    # Load example receipt
    with open("examples/morning-receipt.json", "r") as file:
        example_receipt = json.load(file)

    # Submit the receipt
    response = requests.post(f"{BASE_URL}/receipts/process", json=example_receipt)
    receipt_id = response.json()["id"]

    # Get the points
    points_response = requests.get(f"{BASE_URL}/receipts/{receipt_id}/points")
    assert points_response.status_code == 200
    assert "points" in points_response.json()


def test_all_examples():
    for file_name in os.listdir(EXAMPLES_DIR):
        if file_name.endswith(".json"):
            file_path = os.path.join(EXAMPLES_DIR, file_name)
            with open(file_path, "r") as file:
                example_receipt = json.load(file)
                response = requests.post(
                    f"{BASE_URL}/receipts/process", json=example_receipt
                )
                print(f"{file_name}: {response.status_code} {response.json()}")


def test_invalid_receipt_format():
    # Submit invalid JSON data
    invalid_data = {"not": "a", "receipt": "format"}
    response = requests.post(f"{BASE_URL}/receipts/process", json=invalid_data)
    assert response.status_code == 422


def test_invalid_receipt_data():
    # Modify a valid receipt with invalid data
    with open("examples/morning-receipt.json", "r") as file:
        example_receipt = json.load(file)
    example_receipt["retailer"] = "123!@#$%"  # Invalid retailer name

    response = requests.post(f"{BASE_URL}/receipts/process", json=example_receipt)
    assert response.status_code == 422


def test_get_points_nonexistent_receipt():
    receipt_id = "invalid_id"
    response = requests.get(f"{BASE_URL}/receipts/{receipt_id}/points")
    assert response.status_code == 404


def test_get_points_invalid_id_format():
    # Test invalid ID format (should return 422)
    invalid_id = "invalid_format"
    response = requests.get(f"{BASE_URL}/receipts/{invalid_id}/points")
    assert response.status_code == 404