import re
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage


EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._*+-]+@[a-zA-Z0-9.*-]+\.[a-zA-Z]{2,}"
)
CARD_REGEX = re.compile(r"\b(\d{4})[- ]?\d{4}[- ]?\d{4}[- ]?(\d{4})\b")


def mask_email(email: str) -> str:
    local, domain = email.split("@")

    # mask local part
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

    # mask domain name but keep TLD
    domain_name, tld = domain.rsplit(".", 1)
    masked_domain = "*" * len(domain_name)

    return f"{masked_local}@{masked_domain}.{tld}"

def mask_credit_card(card: str) -> str:
    digits = re.sub(r"\D", "", card)
    return "****-****-****-" + digits[-4:]


class PIIMaskUXMiddleware(AgentMiddleware):
    """
    UX-friendly masking on AI OUTPUT only
    """

    def on_agent_finish(self, result):
        """
        Called after the model generates a response
        """
        message = result.get("messages", [])[-1]

        if isinstance(message, AIMessage) and isinstance(message.content, str):
            # Mask emails
            message.content = EMAIL_REGEX.sub(
                lambda m: mask_email(m.group(0)),
                message.content,
            )

            # Mask credit cards
            message.content = CARD_REGEX.sub(
                lambda m: mask_credit_card(m.group(0)),
                message.content,
            )

        return result
