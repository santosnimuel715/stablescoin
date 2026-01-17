
from ml.llm import call_llm
from typing import Any, Dict, List

def extract_claims(text: str):
    prompt = """
    Extract factual claims from the text.

    Return a JSON array where each item has:
    - claim_text (string)
    - claim_type (fact | prediction | opinion | speculation)
    - sentiment (positive | negative | neutral)

    Only include explicit claims.
    """

    return call_llm(prompt, text)


def analyze_article(title: str, content: str) -> Dict[str, Any]:
    system_prompt = """
    TASK:
    Analyze the given news article and return structured data.

    1. Determine article priority:
    - breaking: urgent, market-moving, hacks, regulation, bans, lawsuits
    - top: high-impact industry news
    - major: important but not urgent
    - normal: everything else

    2. Determine article category as ONE of:
    domestic, international, economy, life, IT, entertainment, sports, science

    Rules:
    - Category must reflect the real-world domain, not the technology itself
    - Blockchain is NOT a category
    - Sports teams, athletes, leagues → sports
    - Research, cryptography, scientific methods → science

    3. Extract ONLY explicit claims from the article.
    Each claim must include:
    - claim_text (string)
    - claim_type (fact | prediction | opinion | speculation)
    - sentiment (positive | negative | neutral)

    4. Translate the article title and content into Japanese.
    - Keep meaning accurate
    - Use natural Japanese news style

    OUTPUT FORMAT (STRICT JSON):
    {
      "priority": "...",
      "category": "...",
      "claims": [
        {
          "claim_text": "...",
          "claim_type": "...",
          "sentiment": "..."
        }
      ],
      "ja": {
        "title": "...",
        "content": "..."
      }
    }
    """

    user_text = f"""
    TITLE:
    {title}

    CONTENT:
    {content}
    """

    return call_llm(system_prompt, user_text)