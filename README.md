# Interview Harvester

A command-line tool to fetch, backfill, and maintain a bank of real-world backend interview questions.

## Features

* Fetches authentic interview questions across multiple rounds (DSA, Debugging, System Design, API Integration, Behavioral)
* Supports customizable prompt templates stored in `prompts.json`
* Avoids duplicates via local fuzzy matching
* Stores questions in a local JSON file (`questions.json`)
* Backfills existing banks with sequential IDs, topics, sources, and timestamps
* Handles API errors and rate limits gracefully

## Prerequisites

* Python 3.8+
* An OpenAI API key (set in `.env` as `OPENAI_API_KEY`)
* `prompts.json` file defining prompt templates
* Install dependencies:

  ```bash
  pip install openai python-dotenv
  ```

## Getting Started

1. **Clone the repo**

   ```bash
   git clone git@github.com:USERNAME/interview-harvester.git
   cd interview-harvester
   ```

2. **Configure environment**

   * Create a `.env` at project root:

     ```dotenv
     OPENAI_API_KEY=sk-...
     QUESTIONS_JSON_PATH=~/questions.json  # optional
     PROMPT_FILE=~/prompts.json            # optional
     ```

3. **Define prompt templates**

   * Edit `prompts.json` (see examples below) to add or modify retrieval strategies.

4. **Run the fetcher**

   * List templates:

     ```bash
     python fetch_questions.py --list
     ```
   * Fetch using a template:

     ```bash
     python fetch_questions.py --template all_rounds
     ```

5. **Schedule daily runs**

   * Add a cron job:

     ```cron
     0 7 * * * /usr/bin/env bash -lc 'python /path/to/fetch_questions.py --template all_rounds >> ~/harvester.log 2>&1'
     ```

## File Structure

```
├── fetch_questions.py   # Main script
├── prompts.json         # JSON of prompt templates
├── questions.json       # Generated question bank
└── .env                 # Environment variables
```

## prompts.json Example

```json
{
  "all_rounds": {
    "system": "You are an expert at retrieving real interview questions for back-end roles.",
    "model": "gpt-3.5-turbo",
    "max_tokens": 400,
    "temperature": 0.7,
    "template": "Please retrieve up to {max_new} actual backend interview questions covering all rounds: {topics}. Format [Company][Stage][Source] Question text."
  },
  "dsa_only": {
    "system": "You retrieve real DSA questions.",
    "template": "Please retrieve up to {max_new} actual DSA interview questions at: {companies}. Format [Company][DSA][Source] Question text."
  }
}
```

## Contributing

Feel free to open issues or submit PRs. Common enhancements:

* Integration with Notion or other databases
* Advanced duplicate detection via embeddings
* Slack/email notifications on new questions

## License

MIT © Prince Raj
