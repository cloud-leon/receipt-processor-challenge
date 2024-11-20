from fastapi import FastAPI, HTTPException, Path, Request, logger
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic.class_validators import validator
from uuid import uuid4
from datetime import date, time
from typing import List, Dict

app = FastAPI()

# In-memory store for receipts and points
receipts_store: Dict[str, dict] = {}
points_store: Dict[str, int] = {}

class InvalidReceiptDataError(Exception):
    pass

class PointsCalculationError(Exception):
    pass

# Models based on OpenAPI specification
from pydantic import BaseModel, Field, validator
class Item(BaseModel):
    shortDescription: str = Field(
        ...,
        example="Mountain Dew 12PK",
        description="A short description of the item."
    )
    price: str = Field(
        ...,
        example="6.49",
        description="The price of the item, formatted as a string with two decimal places."
    )

    @validator("shortDescription")
    def validate_short_description(cls, description: str) -> str:
        """Ensure the description contains only valid characters."""
        if not all(c.isalnum() or c.isspace() or c in {'-', '_'} for c in description):
            raise ValueError(
                "Short description must contain only alphanumeric characters, spaces, hyphens, or underscores."
            )
        return description.strip()

    @validator("price")
    def validate_price(cls, price: str) -> str:
        """Ensure the price is a valid string representing a float with two decimal places."""
        try:
            parsed_price = float(price)
            if parsed_price <= 0:
                raise ValueError("Price must be greater than zero.")
            # Ensure it has exactly two decimal places
            if len(price.split('.')[-1]) != 2:
                raise ValueError("Price must have exactly two decimal places.")
        except ValueError:
            raise ValueError("Price must be a valid number formatted as a string (e.g., '6.49').")
        return price

class Receipt(BaseModel):
    retailer: str = Field(
        ...,
        example="M&M Corner Market",
        description="The name of the retailer or store."
    )
    purchaseDate: date = Field(
        ...,
        example="2022-01-01",
        description="The date of the purchase in YYYY-MM-DD format."
    )
    purchaseTime: time = Field(
        ...,
        example="13:01",
        description="The time of the purchase in 24-hour format (HH:MM)."
    )
    items: List[Item] = Field(
        ...,
        description="A list of at least one purchased item."
    )
    total: str = Field(
        ...,
        example="6.49",
        description="The total amount paid, formatted as a string with two decimal places."
    )

    @validator("retailer")
    def validate_retailer(cls, retailer: str) -> str:
        """Ensure the retailer name contains valid characters."""
        if not all(c.isalnum() or c.isspace() or c in {'-', '&'} for c in retailer):
            raise ValueError(
                "Retailer name must contain only alphanumeric characters, spaces, hyphens, or ampersands."
            )
        return retailer.strip()

    @validator("total")
    def validate_total(cls, total: str) -> str:
        """Ensure the total is a valid string representing a float with two decimal places."""
        try:
            parsed_total = float(total)
            if parsed_total <= 0:
                raise ValueError("Total must be greater than zero.")
            # Ensure it has exactly two decimal places
            if len(total.split('.')[-1]) != 2:
                raise ValueError("Total must have exactly two decimal places.")
        except ValueError:
            raise ValueError("Total must be a valid number formatted as a string (e.g., '6.49').")
        return total


# Endpoint: Submit a receipt
@app.post("/receipts/process", status_code=200)
def process_receipt(receipt: Receipt):
    receipt_id = str(uuid4())
    receipts_store[receipt_id] = receipt.dict()
    points = calculate_points(receipt)
    points_store[receipt_id] = points
    return {"id": receipt_id}

# Endpoint: Get points for a receipt
@app.get("/receipts/{id}/points", status_code=200)
def get_points(id: str = Path(..., regex=r"\S+")):
    if id not in receipts_store:
        raise HTTPException(status_code=404, detail="No receipt found for that ID.")
    return {"points": points_store[id]}

# Points calculation logic
def calculate_points(receipt: Receipt) -> int:
    try:
        # ... existing point calculation logic
        points = 0
        # Rule 1: 1 point per alphanumeric character in the retailer name
        points += sum(c.isalnum() for c in receipt.retailer)
        # Rule 2: 50 points if the total is a round dollar amount with no cents
        total_float = float(receipt.total)
        if total_float.is_integer():
            points += 50
        # Rule 3: 25 points if the total is a multiple of 0.25
        if total_float % 0.25 == 0:
            points += 25
        # Rule 4: 5 points for every two items on the receipt
        points += (len(receipt.items) // 2) * 5
        # Rule 5: If the purchase date is odd, add 6 points
        if receipt.purchaseDate.day % 2 == 1:
            points += 6
        # Rule 6: If the purchase time is between 14:00 and 16:00, add 10 points
        if time(14, 0) <= receipt.purchaseTime < time(16, 0):
            points += 10
        return points

    except ValueError as e:
        logger.error("Error calculating points: %s", str(e))
        raise HTTPException(status_code=400, detail="Error calculating points")
    
@app.exception_handler(InvalidReceiptDataError)
async def handle_invalid_receipt_data(request: Request, exc: InvalidReceiptDataError):
    return JSONResponse(status_code=400, content={"message": str(exc)})