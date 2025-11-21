from google.adk.agents import SequentialAgent
from agents.selector import selector_agent
from agents.enricher import enricher_agent

# Define a local class to avoid "App name mismatch" warning
class MorningDigestPipeline(SequentialAgent):
    pass

# Create the Sequential Pipeline
morning_digest_pipeline = MorningDigestPipeline(
    name="MorningDigestPipeline",
    sub_agents=[selector_agent, enricher_agent],
    description="A pipeline that selects top articles and enriches them with key takeaways."
)

