from pydantic import BaseModel
from agents import function_tool

class DesignDatabaseEntry(BaseModel):
  rooms: list[str]
  design_style: str
  color_palette: list[str]
  furniture: list[str]

@function_tool
async def save_design_data_to_database(data: DesignDatabaseEntry):
  # Simulate a database save with an async sleep
  print("Design data saved to database:", data)

  with open("output/design_output.txt", "w") as f:
    f.write(str(data))