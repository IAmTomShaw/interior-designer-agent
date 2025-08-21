from agents import Agent, Runner, ImageGenerationTool, trace, gen_trace_id, input_guardrail, GuardrailFunctionOutput, RunContextWrapper, TResponseInputItem, InputGuardrailTripwireTriggered, function_tool
from pydantic import BaseModel
from lib.files import retrieve_image_from_resources
import base64
import os
# Guardrail Agent

class FloorplanGuardrailOutput(BaseModel):
  is_not_allowed: bool
  reasoning_response: str

guardrail_agent = Agent(
  name="Floorplan Guardrail Agent",
  instructions="""
  Check if the image that the user has submitted is a valid floorplan and that the user's design preference input is actually relevant to interior design. The user must not as for anything offensive or not safe work work.
""",
  tools=[],
  output_type=FloorplanGuardrailOutput,
)


@input_guardrail
async def floorplan_guardrail(ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
  result = await Runner.run(guardrail_agent, input)

  return GuardrailFunctionOutput(
    output_info=result.final_output,
    tripwire_triggered=result.final_output.is_not_allowed,
  )

# Interior Design Agent

interior_design_agent = Agent(
  name="Interior Design Agent",
  instructions="""
  You are an interior design agent that can generate design images for every room in a home based on the floorplan that is submitted by the user.

  You should approach the problem using this process:  
  1. Identify the rooms in the floorplan image submitted by the user.
  2. Identify the realistic dimensions of each of the rooms in the floorplan.
  3. Plan the layout and design elements for each room based on the user's preferences (take into account the placement of fixed features such as doors and windows which are visible in the floorplan)
  4. Generate 1 image for each room based on the design plan.
  5. Save the interior design details into the database for each room that you have generated. Only save the details of the design after you have generated the image. Save the interior for this entire floorplan in a single database entry. Do not make multiple database entries.

  The user's design preferences will be submitted using the user prompt.Hello tger emy name is tom shaw i. asoftehre devleopet hat siturns ideas intor relaity

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
      "quality": "high",
      "size": "1024x1024",
    })
  ],
  input_guardrails=[
    floorplan_guardrail
  ]
)

async def run_interior_design_agent(style: str, floorplan_image: str) -> None:

  # If the output folder doesn't exist, create it

  os.makedirs("output", exist_ok=True)

  image = retrieve_image_from_resources(floorplan_image)

  formatted_prompt = [{
    "role": "user",
    "content": [
      {
        "type": "input_image",
        "image_url": f"data:image/jpeg;base64,{image}"
      },
      {
        "type": "input_text",
        "text": style
      }
    ],
  }]

  trace_id = gen_trace_id()

  with trace(workflow_name="Image generation example", trace_id=trace_id):
    print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
    try:

      response = await Runner.run(interior_design_agent, formatted_prompt)

      print(response.final_output)

      trace_id = gen_trace_id()

      image_paths = []

      image_count = 0

      for item in response.new_items:
        if (
          item.type == "tool_call_item"
          and item.raw_item.type == "image_generation_call"
          and (img_result := item.raw_item.result)
        ):
          with open(f"output/generated_image_{image_count}.png", "wb") as f:
            f.write(base64.b64decode(img_result))
            image_paths.append(f"output/generated_image_{image_count}.png")
            image_count += 1

      return {
        "image_paths": image_paths,
        "text": response.final_output
      }

    except InputGuardrailTripwireTriggered as e:
      print(f"Tripwire triggered: {e}")
      return None