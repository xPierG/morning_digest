import os
import json
from dotenv import load_dotenv
from dotenv import load_dotenv
from agent import MorningDigestAgent
from feedback import FeedbackManager

# Load environment variables from .env file
load_dotenv()

def generate_markdown_email(selection):
    md_output = "# 🌅 Morning Digest (AI Powered)\n\n"
    md_output += "Buongiorno! Ecco la tua selezione di letture per oggi, curata dall'IA per massimizzare il tuo impatto.\n\n"
    
    for i, doc in enumerate(selection, 1):
        md_output += f"### {i}. {doc['title']}\n"
        md_output += f"**Categoria:** {doc.get('category_label', 'N/A')}\n"
        if 'ai_reasoning' in doc:
            md_output += f"**Perché te lo propongo:** _{doc['ai_reasoning']}_\n\n"
        else:
            md_output += "\n"
            
        md_output += f"{doc.get('summary', 'Nessun riassunto disponibile.')}\n\n"
        md_output += f"[Leggi l'articolo]({doc['source_url']})\n\n"
        # Feedback links (mock links for now)
        md_output += f"`[👍 Mi piace](http://localhost:8000/feedback?id={doc['id']}&action=like)` "
        md_output += f"`[👎 Non mi piace](http://localhost:8000/feedback?id={doc['id']}&action=dislike)`\n\n"
        md_output += "---\n\n"
        
    return md_output

def main():
    print("Starting Morning Digest Agent (AI Mode)...")
    
    # 1. Init components
    agent = MorningDigestAgent()
    feedback_manager = FeedbackManager()
    
    # 2. AI Execution (Fetch + Select)
    print("Running Agent (Tool Use Mode)...")
    top_5 = agent.run()
    
    if not top_5:
        print("No articles selected or error occurred.")
        return

    
    # 4. Generate Report
    report = generate_markdown_email(top_5)
    
    # Output
    print("\n" + "="*30)
    print("GENERATED EMAIL")
    print("="*30 + "\n")
    print(report)
    
    # Save to file for review
    with open("daily_digest.md", "w") as f:
        f.write(report)
    print("\nReport saved to daily_digest.md")

if __name__ == "__main__":
    main()
