import os
import json
import requests
EXAMPLES_DIR = "examples"
import pytest
import requests
import json

BASE_URL = "http://localhost:8080"

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
                    "http://localhost:8080/receipts/process",
                    json=example_receipt,
                )
                print(f"{file_name}: {response.status_code} {response.json()}")


