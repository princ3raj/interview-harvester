#!/usr/bin/env python3
import os
import json
import time
import difflib
from dotenv import load_dotenv
import openai
import difflib
import re
import argparse



# ─── LOAD ENVIRONMENT VARIABLES ─────────────────────────────────────────────────
# Load variables from .env in current directory
load_dotenv()

# ─── CONFIG ─────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY is not set. Please define it in your .env file.")

COMPANIES = [
    # Major FAANG+ & Cloud
    "Google", "Amazon", "Facebook", "Apple", "Microsoft", "Netflix",

    # High-growth & Unicorns
    "Stripe", "Airbnb", "Uber", "Lyft", "DoorDash", "Snapchat", "Pinterest", "Palantir",

    # Enterprise & SaaS
    "Salesforce", "Adobe", "SAP", "Oracle", "ServiceNow", "Atlassian", "Workday", "Slack", "Zoom", "Twilio",

    # Fintech & Crypto
    "Coinbase", "Robinhood", "Revolut", "Wise", "Square", "Chime", "Klarna",

    # E-commerce & Marketplaces
    "Shopify", "eBay", "Alibaba", "JD.com", "Rakuten",

    # Social & Media
    "Twitter", "Snap", "Spotify", "TikTok", "Reddit",

    # Hardware & Infrastructure
    "Intel", "NVIDIA", "Cisco", "Qualcomm", "ARM",

    # Emerging & Regional Giants
    "Tencent", "ByteDance", "Grab", "Gojek", "Nubank", "MercadoLibre"
]

TOPICS = [
    "DSA", "System Design", "Debugging", "API Integration", "Distributed Systems", 
    "Concurrency", "Database", "Networking", "Security", "Operating Systems", 
    "Design Patterns", "Testing", "Performance", "Caching", "Message Queues", 
    "Microservices", "CI/CD", "Monitoring & Observability", "Cloud Infrastructure", 
    "Authentication & Authorization", "Data Modeling", "Fault Tolerance"
]

# Supported OpenAI models for question retrieval
MODELS = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    "gpt-4-32k",
    "gpt-4-turbo",
    "gpt-4-turbo-32k",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4o-mini-instruct"
]

MAX_NEW = 10
JSON_PATH = os.path.expanduser(os.getenv("QUESTIONS_JSON_PATH", "~/questions.json"))
PROMPT_FILE = os.path.expanduser(os.getenv("PROMPT_FILE", "~/prompts.json"))


# ─── INITIALIZE OPENAI ─────────────────────────────────────────────────────────────
openai.api_key = OPENAI_API_KEY

# ─── ARGPARSE ───────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="Fetch backend interview questions based on prompt templates.")
    parser.add_argument("--template", type=str, help="Name of the prompt template to use.")
    parser.add_argument("--list", action="store_true", help="List available prompt templates.")
    return parser.parse_args()

# ─── HELPERS ────────────────────────────────────────────────────────────────────
def load_existing(path=JSON_PATH):
    if not os.path.exists(path): return []
    try:
        with open(path, "r") as f:
            content = f.read().strip()
            data = json.loads(content) if content else []
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_existing(data, path=JSON_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_prompts(path=PROMPT_FILE):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path) as f:
        return json.load(f)


def is_duplicate(q, existing_texts, cutoff=0.8):
    return any(difflib.SequenceMatcher(None, q, ex).ratio() > cutoff for ex in existing_texts)


# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    prompts = load_prompts()
    if args.list:
        print("Available templates:")
        for name in prompts.keys():
            print(f"- {name}")
        return
    if not args.template or args.template not in prompts:
        print("Please specify a valid --template. Use --list to see options.")
        return
    template = prompts[args.template]
    existing = load_existing()
    existing_texts = [e.get("text", "") for e in existing]
    next_id = len(existing) + 1

     # Build prompt from template
    prompt = template["template"].format(
        max_new=MAX_NEW,
        companies=', '.join(COMPANIES),
        topics=', '.join(TOPICS)
    )

    prompt += "\n\nPlease ensure each question is returned as a complete sentence without truncation."
    
    try:
        model=template.get("model", "gpt-3.5-turbo-16k")
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": template.get("system", "You are an expert question retriever.")},
                {"role": "user", "content": prompt}
            ],
            max_tokens=template.get("max_tokens", 400),
            temperature=template.get("temperature", 0.7),
        )
    except Exception as err:
        # Handle rate limit or other API errors gracefully
        print(f"Error fetching questions: {err} with prompt: {prompt}")
        return

    lines = response.choices[0].message.content.strip().split("\n")

    new_entries = []
    for line in lines:
        text = re.sub(r'^\d+\.\s*', '', line).strip().strip('"')
        if not text:
            continue
        tags = re.findall(r"\[([^\]]+)\]", text)
        content = re.sub(r"^(?:\[[^\]]+\])+,?\s*", "", text)
        company = tags[0] if len(tags) > 0 else "Unknown"
        topic = tags[1] if len(tags) > 1 else "Unknown"
        source = tags[2] if len(tags) > 2 else "Unknown"
        q = content.strip().strip('"')
        if q and not is_duplicate(q, existing_texts):
            new_entries.append({
                "id": next_id,
                "company": company,
                "topic": topic,
                "source": source,
                "text": q,
                "fetched_at": time.strftime("%Y-%m-%d")
            })
            existing_texts.append(q)
            next_id += 1

    if new_entries:
        existing.extend(new_entries)
        save_existing(existing)
        for e in new_entries:
            print(f"➕ ({e['id']}) [{e['company']}][{e['topic']}][{e['source']}] {e['text']}")
    else:
        print("✔ No new questions found.")


if __name__ == "__main__":
    main()
