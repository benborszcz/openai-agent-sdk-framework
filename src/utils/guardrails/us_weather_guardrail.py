from pydantic import BaseModel, Field
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

class USWeatherOutput(BaseModel):
    reasoning: str = Field(..., description="The reasoning behind the determination.")
    is_weather_in_us: bool = Field(..., description="True if the user is asking about weather in the US, False otherwise.")
    is_weather: bool = Field(..., description="True if the user is asking about weather, False otherwise.")
    
guardrail_agent = Agent( 
    name="Guardrail check",
    instructions="Make sure the user is not asking about weather outside the US.",
    output_type=USWeatherOutput,
)

@input_guardrail
async def us_weather_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    print(result.final_output)
    return GuardrailFunctionOutput(
        output_info="User is not asking about weather in the US. This is not allowed. Tell the user that this service only supports weather in the US.", 
        tripwire_triggered=(not(result.final_output.is_weather_in_us) and result.final_output.is_weather),
    )