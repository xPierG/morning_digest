import os
import json
import markdown
from dotenv import load_dotenv
from notification import send_digest_email
# Load environment variables from .env file
load_dotenv()

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import morning_digest_pipeline
from datetime import datetime
import asyncio
import traceback

def _convert_to_html_email(markdown_text: str) -> str:
    """
    Converts Markdown to HTML with clean email template and CSS inline.
    """
    # Convert Markdown to HTML
    html_body = markdown.markdown(
        markdown_text,
        extensions=['extra', 'nl2br']
    )
    
    # Wrap in clean HTML template with inline CSS for email compatibility
    html_template = f"""
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h3 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        strong {{
            color: #2c3e50;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        ul {{
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    {html_body}
    <hr>
    <p style="color: #7f8c8d; font-size: 0.9em; text-align: center;">
        Questo digest è stato generato automaticamente da <strong>Morning Digest AI</strong> 🤖
    </p>
</body>
</html>
"""
    return html_template

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
        
        # Convert Markdown to HTML for email
        html_content = _convert_to_html_email(report)
        
        # Send email
        today = datetime.now().strftime("%d/%m/%Y")
        subject = f"🌅 Morning Digest AI - {today}"
        
        success = send_digest_email(subject, html_content)
        
        if success:
            print("\n✅ Email inviata con successo!")
        else:
            print("\n❌ Errore nell'invio email. Controlla i log e le credenziali SMTP.")
    else:
        print("Pipeline finished but no 'final_digest' found in state.")

if __name__ == "__main__":
    main()
