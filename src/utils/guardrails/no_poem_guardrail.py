from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    output_guardrail,
)


class MessageOutput(BaseModel):
    response: str


class PoemDetectionOutput(BaseModel):
    reasoning: str  # brief reasoning why classified as poem or not
    is_poem: bool  # True if the content is (or strongly resembles) a poem


guardrail_agent = Agent(
    name="Poem guardrail",
    instructions=(
        "Determine if the provided text is a poem."
        " Return is_poem=True if the text is primarily poetic (multiple short lines,"
        " deliberate rhyme, meter-like structure, stanza formatting, or explicit user intent to write a poem)."
        " Otherwise return is_poem=False. Provide a concise reasoning field."
    ),
    output_type=PoemDetectionOutput,
)


@output_guardrail
async def no_poem_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput | str
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, str(output), context=ctx.context)
    print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=(
            "Output appears to be a poem."
            if result.final_output.is_poem
            else "Output is not a poem."
        ),
        tripwire_triggered=result.final_output.is_poem,
    )
