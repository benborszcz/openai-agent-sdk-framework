from pydantic import BaseModel, Field
from enum import Enum

class ExampleEnum(str, Enum):
    OPTION_ONE = "Option one"
    OPTION_TWO = "Option two"
    OPTION_THREE = "Option three"

class ExampleStructure(BaseModel):
    example_field: str = Field(..., description="An example field for demonstration purposes. Please put a random short sentence here.")
    example_number: int = Field(..., ge=0, le=100, description="An example number between 0 and 100.")
    example_enum: ExampleEnum = Field(..., description="An example enum field with predefined options.")
    optional_field: str | None = Field(None, description="An optional field that can be omitted.")
