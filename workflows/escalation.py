"""Escalation workflows for handling alerts and events."""


def escalate(event):
    """Return escalation details for a given event."""
    reason = event.get("reason") or event.get("status") or "unknown"
    return {
        "event": event,
        "escalated": True,
        "message": f"Escalation triggered because {reason} requires review.",
    }
