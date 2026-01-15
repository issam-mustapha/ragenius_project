from typing import List
from app.agent.long_memory import UserProfile


def build_user_profile_context(profile: UserProfile) -> str:
    """
    Converts a UserProfile object into a natural-language context
    optimized for LLM understanding.
    """

    if not profile:
        return "No user profile information is available."

    sections: List[str] = []

    # ─────────────────────────────
    # Identity & background
    # ─────────────────────────────
    if profile.name:
        sections.append(f"The user's name is {profile.name}.")
    # else:
    #     sections.append("The user has not shared their name.")

    # if profile.profession:
    #     sections.append(f"They work as a {profile.profession}.")
    # else:
    #     sections.append("Their profession is currently unknown.")

    # if profile.years_experience:
    #     sections.append(
    #         f"They have experience in: {', '.join(profile.years_experience)}."
    #     )

    # # ─────────────────────────────
    # # Skills & interests
    # # ─────────────────────────────
    # if profile.hobbies:
    #     sections.append(
    #         f"Their interests and hobbies include: {', '.join(profile.hobbies)}."
    #     )

    # if profile.languages:
    #     sections.append(
    #         f"They speak the following languages: {', '.join(profile.languages)}."
    #     )

    # # ─────────────────────────────
    # # Learning & communication preferences
    # # ─────────────────────────────
    # if profile.learning_methods:
    #     sections.append(
    #         "They learn best using: "
    #         + ", ".join(profile.learning_methods)
    #         + "."
    #     )

    # if profile.communication_style:
    #     sections.append(
    #         "They prefer communication that is: "
    #         + ", ".join(profile.communication_style)
    #         + "."
    #     )

    # # ─────────────────────────────
    # # Custom preferences
    # # ─────────────────────────────
    # if profile.preferences:
    #     pref_lines = [
    #         f"- {key}: {value}" for key, value in profile.preferences.items()
    #     ]
    #     sections.append(
    #         "Additional user preferences:\n" + "\n".join(pref_lines)
    #     ) 

    return "\n".join(sections)
