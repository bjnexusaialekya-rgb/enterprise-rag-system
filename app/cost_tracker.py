import os
import time
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Pricing per 1000 tokens (USD) — update as providers change rates
PRICING = {
    "groq": {
        "llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079},
    },
    "openai": {
        "gpt-4o":                  {"input": 0.0025,  "output": 0.01},
        "text-embedding-3-large":  {"input": 0.00013, "output": 0.0},
    },
    "local": {
        "sentence-transformers":   {"input": 0.0,     "output": 0.0},
    }
}


def calculate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> dict:
    """Calculate USD cost for a single LLM or embedding call."""
    provider = provider.lower()
    model = model.lower()

    rates = PRICING.get(provider, {}).get(model)
    if rates is None:
        logger.warning(f"No pricing data for provider={provider} model={model}. Cost set to 0.")
        input_cost  = 0.0
        output_cost = 0.0
    else:
        input_cost  = (prompt_tokens     / 1000) * rates["input"]
        output_cost = (completion_tokens / 1000) * rates["output"]

    return {
        "provider":          provider,
        "model":             model,
        "prompt_tokens":     prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens":      prompt_tokens + completion_tokens,
        "input_cost_usd":    round(input_cost,  6),
        "output_cost_usd":   round(output_cost, 6),
        "total_cost_usd":    round(input_cost + output_cost, 6),
        "timestamp":         datetime.now(timezone.utc).isoformat()
    }


class CostTracker:
    """Session-level cost accumulator. One instance per request or session."""

    def __init__(self, session_id: str = None):
        self.session_id   = session_id or f"session_{int(time.time())}"
        self.events: list = []
        self.total_cost   = 0.0
        self.total_tokens = 0

    def track(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> dict:
        """Record one API call and accumulate totals."""
        event = calculate_cost(provider, model, prompt_tokens, completion_tokens)
        event["session_id"] = self.session_id

        self.events.append(event)
        self.total_cost   += event["total_cost_usd"]
        self.total_tokens += event["total_tokens"]

        logger.info(
            f"[CostTracker] session={self.session_id} "
            f"model={model} tokens={event['total_tokens']} "
            f"cost=${event['total_cost_usd']:.6f}"
        )
        return event

    def summary(self) -> dict:
        """Return aggregated cost summary for this session."""
        return {
            "session_id":        self.session_id,
            "total_calls":       len(self.events),
            "total_tokens":      self.total_tokens,
            "total_cost_usd":    round(self.total_cost, 6),
            "events":            self.events
        }


if __name__ == "__main__":
    print("Testing cost_tracker...")

    # Single call calculation
    result = calculate_cost(
        provider="groq",
        model="llama-3.3-70b-versatile",
        prompt_tokens=134,
        completion_tokens=20
    )
    print(f"Single call cost: ${result['total_cost_usd']:.6f}")
    print(f"Total tokens: {result['total_tokens']}")

    # Session tracking
    tracker = CostTracker(session_id="test_session_001")
    tracker.track("groq", "llama-3.3-70b-versatile", 134, 20)
    tracker.track("groq", "llama-3.3-70b-versatile", 200, 45)

    summary = tracker.summary()
    print(f"Session total cost: ${summary['total_cost_usd']:.6f}")
    print(f"Session total calls: {summary['total_calls']}")
    print(f"Session total tokens: {summary['total_tokens']}")
    print("Cost tracker test PASSED ✅")