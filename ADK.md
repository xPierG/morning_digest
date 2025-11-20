# Google Agent Development Kit (ADK) Documentation

## Introduction

The Google Agent Development Kit (ADK) is a comprehensive framework for building sophisticated AI agent systems using Large Language Models. ADK enables developers to create autonomous agents that can reason, use tools, and collaborate in multi-agent architectures. The framework supports multiple agent types including LLM-powered agents for intelligent decision-making, workflow agents for deterministic process control, and custom agents for specialized logic. ADK provides a unified API across Python and Java, making it accessible to a wide range of developers and use cases.

ADK simplifies the complexity of building agent systems by providing built-in session management, state handling, event streaming, and integration with multiple LLM providers including Google Gemini, OpenAI, and Anthropic Claude. The framework excels at orchestrating complex workflows where agents need to execute tasks sequentially, in parallel, or iteratively with loop-based refinement. Additionally, ADK implements the Agent2Agent (A2A) Protocol, enabling seamless communication between distributed agent services across network boundaries, making it ideal for building scalable, microservices-based AI applications.

## Core APIs and Functions

### Creating an LLM Agent

Create an intelligent agent powered by a Large Language Model with instructions, tools, and state management.

```python
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Define a tool function
def get_capital_city(country: str) -> str:
    """Retrieves the capital city for a given country."""
    capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
    return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

# Create the agent
capital_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="capital_agent",
    description="Answers user questions about the capital city of a given country.",
    instruction="""You are an agent that provides the capital city of a country.
When a user asks for the capital of a country:
1. Identify the country name from the user's query.
2. Use the `get_capital_city` tool to find the capital.
3. Respond clearly to the user, stating the capital city.
Example Query: "What's the capital of France?"
Example Response: "The capital of France is Paris."
""",
    tools=[get_capital_city],
    output_key="capital_result"
)

# Setup session and runner
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="capital_app",
    user_id="user123",
    session_id="session001"
)

runner = Runner(
    agent=capital_agent,
    app_name="capital_app",
    session_service=session_service
)

# Run the agent
content = types.Content(role='user', parts=[types.Part(text="What's the capital of France?")])
events = runner.run(user_id="user123", session_id="session001", new_message=content)

for event in events:
    if event.is_final_response() and event.content:
        print(event.content.parts[0].text)
# Output: "The capital of France is Paris."
```

### Creating a Sequential Agent Workflow

Execute multiple agents in a fixed, deterministic sequence for structured processes.

```python
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Define sub-agents
code_writer_agent = LlmAgent(
    name="CodeWriterAgent",
    model="gemini-2.0-flash",
    instruction="""You are a Python Code Generator.
Based on the user's request, write Python code that fulfills the requirement.
Output only the complete Python code block, enclosed in triple backticks.
Do not add any other text before or after the code block.""",
    description="Writes initial Python code based on a specification.",
    output_key="generated_code"
)

code_reviewer_agent = LlmAgent(
    name="CodeReviewerAgent",
    model="gemini-2.0-flash",
    instruction="""You are an expert Python Code Reviewer.
**Code to Review:**
```python
{generated_code}
```

Review the code for correctness, readability, efficiency, edge cases, and best practices.
Provide feedback as a concise, bulleted list focusing on improvements.
If the code is excellent, state: "No major issues found."
Output only the review comments or the "No major issues" statement.""",
    description="Reviews code and provides feedback.",
    output_key="review_comments"
)

code_refactorer_agent = LlmAgent(
    name="CodeRefactorerAgent",
    model="gemini-2.0-flash",
    instruction="""You are a Python Code Refactoring AI.
**Original Code:**
```python
{generated_code}
```

**Review Comments:**
{review_comments}

Apply the suggestions to refactor the original code.
If review says "No major issues found," return the original code unchanged.
Output only the final, refactored Python code block in triple backticks.""",
    description="Refactors code based on review comments.",
    output_key="refactored_code"
)

# Create the sequential pipeline
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
    description="Executes a sequence of code writing, reviewing, and refactoring."
)

# Run the pipeline
runner = InMemoryRunner(code_pipeline_agent, app_name="code_pipeline")
session = runner.session_service().create_session("code_pipeline", "user456").blocking_get()

user_message = types.Content.from_parts(
    types.Part.from_text("Write a function to calculate factorial")
)
event_stream = runner.run_async("user456", session.id(), user_message)

for event in event_stream:
    if event.final_response():
        print(event.stringify_content())
```

### Creating a Parallel Agent Workflow

Execute multiple agents concurrently for independent tasks to maximize performance.

```python
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import GoogleSearchTool

# Create research agents that run in parallel
researcher_agent_1 = LlmAgent(
    name="RenewableEnergyResearcher",
    model="gemini-2.0-flash",
    instruction="""Research the latest advancements in 'renewable energy sources'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output only the summary.""",
    description="Researches renewable energy sources.",
    tools=[GoogleSearchTool()],
    output_key="renewable_energy_result"
)

researcher_agent_2 = LlmAgent(
    name="EVResearcher",
    model="gemini-2.0-flash",
    instruction="""Research the latest developments in 'electric vehicle technology'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output only the summary.""",
    description="Researches electric vehicle technology.",
    tools=[GoogleSearchTool()],
    output_key="ev_technology_result"
)

researcher_agent_3 = LlmAgent(
    name="CarbonCaptureResearcher",
    model="gemini-2.0-flash",
    instruction="""Research the current state of 'carbon capture methods'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output only the summary.""",
    description="Researches carbon capture methods.",
    tools=[GoogleSearchTool()],
    output_key="carbon_capture_result"
)

# Create parallel agent to run all researchers concurrently
parallel_research_agent = ParallelAgent(
    name="ParallelWebResearchAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
    description="Runs multiple research agents in parallel to gather information."
)

# Create merger agent to synthesize results
merger_agent = LlmAgent(
    name="SynthesisAgent",
    model="gemini-2.0-flash",
    instruction="""Synthesize the following research summaries into a structured report.

**Input Summaries:**
* **Renewable Energy:** {renewable_energy_result}
* **Electric Vehicles:** {ev_technology_result}
* **Carbon Capture:** {carbon_capture_result}

Output a structured report with headings for each topic and a conclusion.""",
    description="Combines research findings from parallel agents."
)

# Orchestrate: first run parallel research, then merge
pipeline = SequentialAgent(
    name="ResearchAndSynthesisPipeline",
    sub_agents=[parallel_research_agent, merger_agent],
    description="Coordinates parallel research and synthesizes the results."
)

# Run the pipeline
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(pipeline, app_name="research_app")
session = runner.session_service().create_session("research_app", "user789").blocking_get()

user_message = types.Content.from_parts(
    types.Part.from_text("Research sustainable technology advancements")
)
event_stream = runner.run_async("user789", session.id(), user_message)

for event in event_stream:
    if event.final_response():
        print(event.stringify_content())
```

### Creating a Loop Agent for Iterative Refinement

Execute agents repeatedly until a termination condition is met for iterative improvement workflows.

```python
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import ToolContext

# Define exit loop tool
def exit_loop(tool_context: ToolContext):
    """Call this function when critique indicates no further changes are needed."""
    print(f"[Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}

# Initial writer
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model="gemini-2.0-flash",
    include_contents='none',
    instruction="""You are a Creative Writing Assistant.
Write the first draft of a short story (2-4 sentences) on the topic: {topic}
Output only the story text. Do not add introductions or explanations.""",
    description="Writes the initial document draft based on the topic.",
    output_key="current_document"
)

# Critic agent
critic_agent_in_loop = LlmAgent(
    name="CriticAgent",
    model="gemini-2.0-flash",
    include_contents='none',
    instruction="""You are a Constructive Critic AI reviewing a short document.

**Document to Review:**
```
{current_document}
```

Review the document for clarity, engagement, and basic coherence.
IF you identify 1-2 clear and actionable ways to improve it, provide specific suggestions.
ELSE IF the document is coherent and addresses the topic adequately, respond exactly with:
"No major issues found."

Output only the critique OR the exact completion phrase.""",
    description="Reviews the current draft.",
    output_key="criticism"
)

# Refiner agent
refiner_agent_in_loop = LlmAgent(
    name="RefinerAgent",
    model="gemini-2.0-flash",
    include_contents='none',
    instruction="""You are a Creative Writing Assistant refining a document.

**Current Document:**
```
{current_document}
```
**Critique:** {criticism}

IF the critique is exactly "No major issues found.":
    Call the 'exit_loop' function. Do not output any text.
ELSE:
    Apply the suggestions to improve the document. Output only the refined document text.""",
    description="Refines the document based on critique, or exits loop.",
    tools=[exit_loop],
    output_key="current_document"
)

# Create refinement loop
refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[critic_agent_in_loop, refiner_agent_in_loop],
    max_iterations=5
)

# Create overall pipeline
pipeline = SequentialAgent(
    name="IterativeWritingPipeline",
    sub_agents=[initial_writer_agent, refinement_loop],
    description="Writes an initial document and iteratively refines it."
)

# Run the pipeline
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService

runner = InMemoryRunner(pipeline, app_name="writing_app")
session = runner.session_service().create_session(
    "writing_app",
    "user_writer",
    state={"topic": "a brave kitten exploring a haunted house"}
).blocking_get()

user_message = types.Content.from_parts(
    types.Part.from_text("Generate and refine a story")
)
event_stream = runner.run_async("user_writer", session.id(), user_message)

for event in event_stream:
    if event.final_response():
        print(event.stringify_content())
```

### Creating a Custom Agent with Conditional Logic

Extend BaseAgent to implement custom orchestration logic beyond predefined workflow patterns.

```python
from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator
from typing_extensions import override

class StoryFlowAgent(BaseAgent):
    """Custom agent for story generation with conditional regeneration based on tone."""

    story_generator: LlmAgent
    critic: LlmAgent
    reviser: LlmAgent
    grammar_check: LlmAgent
    tone_check: LlmAgent
    loop_agent: LoopAgent
    sequential_agent: SequentialAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        story_generator: LlmAgent,
        critic: LlmAgent,
        reviser: LlmAgent,
        grammar_check: LlmAgent,
        tone_check: LlmAgent,
    ):
        loop_agent = LoopAgent(
            name="CriticReviserLoop",
            sub_agents=[critic, reviser],
            max_iterations=2
        )
        sequential_agent = SequentialAgent(
            name="PostProcessing",
            sub_agents=[grammar_check, tone_check]
        )

        super().__init__(
            name=name,
            story_generator=story_generator,
            critic=critic,
            reviser=reviser,
            grammar_check=grammar_check,
            tone_check=tone_check,
            loop_agent=loop_agent,
            sequential_agent=sequential_agent,
            sub_agents=[story_generator, loop_agent, sequential_agent]
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Custom orchestration logic with conditional regeneration."""

        # Step 1: Initial story generation
        async for event in self.story_generator.run_async(ctx):
            yield event

        if "current_story" not in ctx.session.state:
            return

        # Step 2: Critic-reviser loop
        async for event in self.loop_agent.run_async(ctx):
            yield event

        # Step 3: Grammar and tone check
        async for event in self.sequential_agent.run_async(ctx):
            yield event

        # Step 4: Conditional regeneration based on tone
        tone_check_result = ctx.session.state.get("tone_check_result")

        if tone_check_result == "negative":
            # Regenerate story if tone is negative
            async for event in self.story_generator.run_async(ctx):
                yield event

# Define sub-agents
story_generator = LlmAgent(
    name="StoryGenerator",
    model="gemini-2.0-flash",
    instruction="Write a short story (around 100 words) on: {topic}",
    output_key="current_story"
)

critic = LlmAgent(
    name="Critic",
    model="gemini-2.0-flash",
    instruction="Review the story: {current_story}. Provide 1-2 sentences of constructive criticism.",
    output_key="criticism"
)

reviser = LlmAgent(
    name="Reviser",
    model="gemini-2.0-flash",
    instruction="Revise the story: {current_story}, based on criticism: {criticism}. Output only the revised story.",
    output_key="current_story"
)

grammar_check = LlmAgent(
    name="GrammarCheck",
    model="gemini-2.0-flash",
    instruction="Check grammar of: {current_story}. Output suggested corrections or 'Grammar is good!'",
    output_key="grammar_suggestions"
)

tone_check = LlmAgent(
    name="ToneCheck",
    model="gemini-2.0-flash",
    instruction="Analyze tone of: {current_story}. Output only one word: 'positive', 'negative', or 'neutral'.",
    output_key="tone_check_result"
)

# Create custom agent
story_flow_agent = StoryFlowAgent(
    name="StoryFlowAgent",
    story_generator=story_generator,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check
)

# Run the custom agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="story_app",
    user_id="user_story",
    session_id="story_session",
    state={"topic": "a lonely robot finding a friend"}
)

runner = Runner(agent=story_flow_agent, app_name="story_app", session_service=session_service)

content = types.Content(role='user', parts=[types.Part(text="Generate a story")])
events = runner.run_async(user_id="user_story", session_id="story_session", new_message=content)

async for event in events:
    if event.is_final_response() and event.content:
        print(event.content.parts[0].text)
```

### Exposing an Agent via Agent2Agent (A2A) Protocol

Convert an existing ADK agent to be accessible over the network using the A2A protocol.

```python
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import FunctionTool

# Define tool functions
def roll_die(sides: int) -> int:
    """Roll a die and return the rolled result."""
    import random
    return random.randint(1, sides)

async def check_prime(nums: list[int]) -> str:
    """Check if given numbers are prime."""
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True

    results = [f"{n} is {'prime' if is_prime(n) else 'not prime'}" for n in nums]
    return ", ".join(results)

# Create the agent to be exposed
hello_world_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world_agent',
    description='Agent that can roll dice and check prime numbers.',
    instruction="""I roll dice and answer questions about dice rolls.
I can roll dice of different sizes.
When asked to roll a die, I must call the roll_die tool with the number of sides.
When checking prime numbers, call the check_prime tool with a list of integers.
When asked to roll a die and check primes:
1. First call roll_die to get a roll.
2. After getting the result, call check_prime with the result.
3. Include the roll_die result in my response.""",
    tools=[roll_die, check_prime]
)

# Expose the agent as an A2A service
a2a_app = to_a2a(hello_world_agent, port=8001)

# Start the server with uvicorn from command line:
# uvicorn module.path:a2a_app --host localhost --port 8001

# Verify it's running by visiting:
# http://localhost:8001/.well-known/agent-card.json
```

### Consuming a Remote Agent via A2A Protocol

Connect to and use a remote agent exposed via A2A from within your local agent.

```python
from google.adk import Agent
from google.adk.a2a import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Create a RemoteA2aAgent that connects to the exposed A2A service
remote_prime_agent = RemoteA2aAgent(
    name="remote_prime_checker",
    agent_card_url="http://localhost:8001/.well-known/agent-card.json",
    description="Remote agent that checks if numbers are prime via A2A protocol"
)

# Define a local tool
def roll_die(sides: int) -> int:
    """Roll a die locally."""
    import random
    return random.randint(1, sides)

# Create root agent that uses both local and remote tools
root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    description='Main agent that coordinates local and remote operations',
    instruction="""I can roll dice locally and check prime numbers via a remote agent.

When user asks to roll a die, use the roll_die tool.
When user asks about prime numbers, use the remote_prime_checker agent.
When user asks to roll and check primes:
1. First roll the die using roll_die
2. Then check if it's prime using remote_prime_checker
3. Report both results to the user""",
    tools=[roll_die, remote_prime_agent]
)

# Setup and run the agent
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="a2a_root",
    user_id="user_a2a",
    session_id="a2a_session"
)

runner = Runner(agent=root_agent, app_name="a2a_root", session_service=session_service)

# Interact with the agent
content = types.Content(
    role='user',
    parts=[types.Part(text="Roll a 10-sided die and check if it's prime")]
)

events = runner.run(user_id="user_a2a", session_id="a2a_session", new_message=content)

for event in events:
    if event.is_final_response() and event.content:
        print(event.content.parts[0].text)
        # Output example:
        # "I rolled an 7 for you."
        # "7 is a prime number."
```

### Using Structured Input and Output Schemas

Define strict JSON schemas for agent inputs and outputs for type safety and integration.

```python
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

# Define schemas
class CountryInput(BaseModel):
    country: str = Field(description="The country to get information about.")

class CapitalInfoOutput(BaseModel):
    capital: str = Field(description="The capital city of the country.")
    population_estimate: str = Field(description="An estimated population of the capital city.")

# Create agent with schemas
structured_info_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="structured_info_agent",
    description="Provides capital and estimated population in JSON format.",
    instruction="""You are an agent that provides country information.
The user will provide the country name in JSON format like {"country": "country_name"}.
Respond ONLY with a JSON object matching this schema:
{
  "capital": "capital city name",
  "population_estimate": "estimated population"
}
Use your knowledge to determine the capital and estimate the population.""",
    input_schema=CountryInput,
    output_schema=CapitalInfoOutput,
    output_key="structured_info_result"
)

# Run the agent
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(structured_info_agent, app_name="structured_app")
session = runner.session_service().create_session("structured_app", "user_struct").blocking_get()

# Input must match the input schema
user_message = types.Content.from_parts(
    types.Part.from_text('{"country": "France"}')
)

event_stream = runner.run_async("user_struct", session.id(), user_message)

for event in event_stream:
    if event.final_response():
        print(event.stringify_content())
        # Output: {"capital": "Paris", "population_estimate": "2.2 million"}

# Access the structured result from session state
final_session = runner.session_service().get_session(
    "structured_app", "user_struct", session.id()
).blocking_get()

result = final_session.state().get("structured_info_result")
print(result)  # JSON string conforming to CapitalInfoOutput schema
```

### Using Built-in Planner for Multi-Step Reasoning

Enable advanced planning and reasoning capabilities using Gemini's thinking feature or PlanReAct pattern.

```python
from google.adk import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import datetime
from zoneinfo import ZoneInfo

# Define tools
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city."""
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C (77°F)."
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available."
        }

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    if city.lower() == "new york":
        tz = ZoneInfo("America/New_York")
        now = datetime.datetime.now(tz)
        return {
            "status": "success",
            "report": f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z")}'
        }
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}."
        }

# Create planner with thinking config
thinking_config = types.ThinkingConfig(
    include_thoughts=True,
    thinking_budget=256
)

planner = BuiltInPlanner(thinking_config=thinking_config)

# Create agent with planner
agent = Agent(
    model="gemini-2.5-flash",
    name="weather_and_time_agent",
    instruction="You are an agent that returns time and weather information.",
    planner=planner,
    tools=[get_weather, get_current_time]
)

# Setup and run
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="weather_app",
    user_id="user_planner",
    session_id="session_planner"
)

runner = Runner(agent=agent, app_name="weather_app", session_service=session_service)

content = types.Content(
    role='user',
    parts=[types.Part(text="If it's raining in New York right now, what is the current temperature?")]
)

events = runner.run(user_id="user_planner", session_id="session_planner", new_message=content)

for event in events:
    print(f"\nEvent: {event}")
    if event.is_final_response() and event.content:
        print("\nFinal Answer:")
        print(event.content.parts[0].text)
        # Agent will show its planning/thinking process and then answer
```

### Configuring LLM Generation Parameters

Control temperature, max tokens, safety settings, and other generation parameters for fine-tuned responses.

```python
from google.adk.agents import LlmAgent
from google.genai import types

# Create agent with custom generation config
agent = LlmAgent(
    model="gemini-2.0-flash",
    name="precise_agent",
    instruction="You are a precise, factual assistant. Provide concise, accurate answers.",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,  # More deterministic output (0.0-1.0)
        max_output_tokens=250,  # Limit response length
        top_p=0.95,  # Nucleus sampling parameter
        top_k=40,  # Top-k sampling parameter
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            )
        ]
    )
)

# Use the agent
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(agent, app_name="precise_app")
session = runner.session_service().create_session("precise_app", "user_precise").blocking_get()

user_message = types.Content.from_parts(
    types.Part.from_text("Explain quantum computing in simple terms")
)

event_stream = runner.run_async("user_precise", session.id(), user_message)

for event in event_stream:
    if event.final_response():
        print(event.stringify_content())
        # Output will be concise, deterministic, and within 250 tokens
```

## Summary and Integration

The Agent Development Kit provides a comprehensive framework for building production-ready AI agent systems. Its primary use cases span from simple single-agent applications like chatbots and Q&A systems to complex multi-agent architectures for enterprise workflows. Common applications include customer service automation where multiple specialized agents handle different domains, document processing pipelines with sequential validation and enrichment steps, research and analysis systems that gather information from multiple sources in parallel, and iterative content generation workflows that refine outputs through multiple revision cycles. The framework's built-in session management and state handling make it particularly well-suited for conversational applications that need to maintain context across multiple turns.

ADK's integration patterns are designed for flexibility and scalability. Developers can start with monolithic applications using local sub-agents and progressively decompose them into distributed microservices using the A2A Protocol as systems grow. The framework integrates seamlessly with existing infrastructure through its support for multiple LLM providers (Gemini, OpenAI, Anthropic), custom tool implementations for API integrations, and standard HTTP/REST interfaces for A2A communication. State management can be customized from the default in-memory implementation to production-grade solutions using Redis or databases. The event streaming architecture allows real-time monitoring and logging of agent behavior, making it straightforward to implement observability, debugging, and quality assurance workflows. Whether building a single intelligent agent or orchestrating dozens of specialized agents across network boundaries, ADK provides the foundational abstractions and production-ready components needed for modern AI application development.
