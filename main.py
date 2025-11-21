import os
import json
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import morning_digest_pipeline
from datetime import datetime
import asyncio
import traceback

def generate_markdown_email(articles):
    """
    Generates a Markdown email report from the list of articles.
    """
    today = datetime.now().strftime("%d/%m/%Y")
    md_output = f"# 🌅 Morning Digest (AI Powered) - {today}\n\n"
    md_output += f"Buongiorno! Ecco la tua selezione di letture per oggi, curata dall'IA per massimizzare il tuo impatto.\n\n"
    
    if not articles:
        md_output += "Nessun articolo trovato o errore durante l'esecuzione.\n"
        return md_output

    for i, doc in enumerate(articles, 1):
        md_output += f"### {i}. {doc['title']}\n"
        md_output += f"**Categoria:** {doc['category_label']}\n\n"
        
        if 'reasoning' in doc:
            md_output += f"**Perché te lo propongo:** _{doc['reasoning']}_\n\n"
        else:
            md_output += "\n"
            
        # Key Takeaways (if enriched)
        if 'key_takeaways' in doc and doc['key_takeaways']:
            md_output += "**Key Takeaways:**\n"
            for point in doc['key_takeaways']:
                md_output += f"*   {point}\n"
            md_output += "\n"
            
        md_output += f"{doc.get('summary', 'Nessun riassunto disponibile.')}\n\n"
        md_output += f"[Leggi l'articolo]({doc['source_url']})\n\n"
        md_output += "---\n\n"
        
    return md_output

def main():
    print("="*30)
    print("Starting Morning Digest Agent (ADK Mode)...")
    print("="*30 + "\n")
    
    async def run_agent():
        try:
            # Setup ADK Runner
            runner = InMemoryRunner(agent=morning_digest_pipeline, app_name="morning_digest")
            
            # Access the internal session service
            session_service = runner.session_service
            
            # Create session (awaiting the coroutine)
            session = await session_service.create_session(
                app_name="morning_digest",
                user_id="caio_user",
                session_id="daily_session"
            )
            
            print("Running Agent Pipeline...")
            
            # Trigger the pipeline
            user_message = types.Content(
                parts=[types.Part.from_text(text="Start Morning Digest generation.")]
            )
            
            async for event in runner.run_async(user_id="caio_user", session_id=session.id, new_message=user_message):
                pass
            
            # Retrieve final state from session
            final_session = await session_service.get_session(app_name="morning_digest", user_id="caio_user", session_id=session.id)
            return final_session.state.get("final_digest")

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            traceback.print_exc()
            return None

    # Run the async agent
    result_json = asyncio.run(run_agent())
    
    if result_json:
        # Parse if it's a string
        if isinstance(result_json, str):
            # Basic Markdown cleanup
            if result_json.startswith("```json"):
                result_json = result_json[7:]
            if result_json.endswith("```"):
                result_json = result_json[:-3]
            
            # Robust parsing
            try:
                data = json.loads(result_json)
            except json.JSONDecodeError as e:
                print(f"Warning: JSON Decode Error ({e}). Attempting to repair...")
                # Common fix for "Invalid \escape": escape backslashes that aren't valid JSON escapes
                # This is a simple heuristic: replace \ with \\ if not followed by " or \ or / or b or f or n or r or t or u
                import re
                # This regex finds backslashes that are NOT followed by valid escape chars
                cleaned_json = re.sub(r'\\(?![/u"\\bfnrt])', r'\\\\', result_json)
                try:
                    data = json.loads(cleaned_json)
                    print("Repair successful.")
                except json.JSONDecodeError:
                    print("Repair failed. Raw output:")
                    print(result_json)
                    raise
        else:
            data = result_json
            
        articles = data.get("selection", [])
        
        report = generate_markdown_email(articles)
        print(report)
        
        # Save to file
        with open("daily_digest.md", "w") as f:
            f.write(report)
        print("\nReport saved to daily_digest.md")
    else:
        print("Pipeline finished but no 'final_digest' found in state.")

if __name__ == "__main__":
    main()
