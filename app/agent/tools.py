from langchain.tools import tool, ToolRuntime
from app.agent.context import Context
from pypdf import PdfReader
from app.agent.storage_utils import save_user_image, ocr_image
import os


@tool
def answer_based_on_image(
    runtime: ToolRuntime[Context],
    file_bytes: bytes,
    query: str,
    filename: str | None = None
) -> str:
    """
    Analyzes a user-uploaded image by extracting text via OCR and generating
    a professional response based on the user's query.

    If the image contains an exercise or problem, it will be solved step by step.

    Args:
        runtime: Agent execution context (user/session data)
        file_bytes: Raw bytes of the uploaded image
        query: User question related to the image
        filename: Optional original filename

    Returns:
        A combined prompt containing extracted text and user intent.
    """
    user_id = runtime.context.user_id
    image_path = save_user_image(user_id, file_bytes, filename)
    image_text = ocr_image(image_path)

    return f"""
User question:
{query}

Extracted text from image:
{image_text}

Instructions:
- Detect if this is an exercise or problem
- Solve it if needed
- Explain clearly and professionally
"""


@tool
def summarize_user_pdf(
    runtime: ToolRuntime[Context],
    pdf_name: str
) -> str:
    """
    Summarizes a user-uploaded PDF document in a clear and structured way.

    Args:
        runtime: Agent execution context
        pdf_name: Name of the PDF file stored for the user

    Returns:
        A structured summarization prompt for the LLM.
    """
    user_id = runtime.context.user_id
    pdf_path = f"storage/users/user_{user_id}/pdfs/{pdf_name}"

    if not os.path.exists(pdf_path):
        return "PDF not found."

    reader = PdfReader(pdf_path)
    text = "".join(
        page.extract_text() + "\n"
        for page in reader.pages
        if page.extract_text()
    )[:15000]

    return f"""
You are a professional document analyst.

Provide a clear and structured summary:
- Main topics
- Key ideas
- Important conclusions

Document content:
{text}
"""


@tool
def summarize_text(
    runtime: ToolRuntime[Context],
    text: str
) -> str:
    """
    Summarizes raw text provided directly by the user.

    Args:
        runtime: Agent execution context
        text: Text to summarize

    Returns:
        A professional summarization prompt.
    """
    text = text.strip()[:15000]

    if len(text) < 200:
        return "Text too short to summarize."

    return f"""
You are a professional summarization assistant.

Instructions:
- Summarize clearly and concisely
- Use bullet points
- Highlight key ideas
- Do not add external information

Content:
{text}
"""
