from agents import Agent, Runner, ImageGenerationTool, input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, RunContextWrapper
from lib.files import retrieve_image_from_resources, open_file
import base64
from pydantic import BaseModel

from lib.tools import save_design_data_to_database
import os

class GuardrailAgentOutput(BaseModel):
  is_not_allowed: bool
  reason: str | None

guardrail_agent = Agent(
  name="Floorplan Checker Agent",
  instructions=""""
    Check if the image that the user has submitted is a valid floorplan and that the user's design preference input is actually relevant to interior design. The user must not ask for anything offensive or not safe for work.
  """,
  tools=[],
  output_type=GuardrailAgentOutput
)

@input_guardrail
async def guardrail_function(ctx: RunContextWrapper, agent: Agent, input_data: str) -> GuardrailFunctionOutput:
  result = await Runner.run(guardrail_agent, input_data)

  return GuardrailFunctionOutput(
    output_info=result.final_output.reason,
    tripwire_triggered=result.final_output.is_not_allowed
  )

class DesignOutput(BaseModel):
  rooms: list[str]
  design_style: str
  color_palette: list[str]
  furniture: list[str]
  description_of_interior_design: str

my_agent = Agent(
  name="Interior Design Agent",
  instructions="""
  You are an interior design agent that can generate design images for every room in a home based on the floorplan that is submitted by the user.

  You should approach the problem using this process:  
  1. Identify the rooms in the floorplan image submitted by the user.
  2. Identify the realistic dimensions of each of the rooms in the floorplan.
  3. Plan the layout and design elements for each room based on the user's preferences (take into account the placement of fixed features such as doors and windows which are visible in the floorplan)
  4. Generate 1 image for each room based on the design plan.
  5. Save the interior design details into the database for each room that you have generated. Only save the details of the design after you have generated the image. Save the interior for this entire floorplan in a single database entry. Do not make multiple database entries. You must use the tool `save_design_data_to_database` to do this.

  The user's design preferences will be submitted using the user prompt.

  Image Generation guidelines:
  - Ensure that the images are relevant to the floorplan
  - Ensure that the images are from a camera perspective that showcases the entire room
  - Do not add in windows or doors where they do not exist in the floorplan
  - Do not generate individual images of hallways (these are not required)
  - Only generate a maximum of 5 images in total

  Output:
  You should return the final output of the agent, including the generated images. Do not output text links to the images in the final output.
  """,
  tools=[
    ImageGenerationTool({
      "type": "image_generation",
      "output_format": "png",
      "quality": "low",
      "size": "1024x1024"
    }),
    save_design_data_to_database
  ],
  model="gpt-4.1",
  input_guardrails=[
    guardrail_function
  ],
  output_type=DesignOutput
)

async def run_agent(design_style: str, floorplan_image: str):

  os.makedirs("output", exist_ok=True)

  image = retrieve_image_from_resources(floorplan_image)

  formatted_input = [{
    "role": "user",
    "content": [
      {
        "type": "input_image",
        "image_url": f"data:image/jpeg;base64,{image}"
      },
      {
        "type": "input_text",
        "text": design_style
      }
    ]
  }]

  try:


    result = await Runner.run(my_agent, formatted_input)

    print("Final output:", result.final_output)

    print("Full run details:", result)

    image_paths = []

    image_count = 0

    for item in result.new_items:
      if (
        item.type == "tool_call_item"
        and item.raw_item.type == "image_generation_call"
        and (img_result := item.raw_item.result)
      ):
        with open(f"output/generated_image_{image_count}.png", "wb") as f:
          f.write(base64.b64decode(img_result))
          image_paths.append(f"output/generated_image_{image_count}.png")
          image_count += 1
          open_file(f"output/generated_image_{image_count}.png")

    return {
      "image_paths": image_paths,
      "final_output": result.final_output
    }

  except InputGuardrailTripwireTriggered as e:
    print("Input guardrail triggered:", e)