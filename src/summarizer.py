import os
import time

from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import SummaryConfig
from src.models import Paper, SummarizedPaper

GEMINI_MODEL = "gemini-2.0-flash"
REQUEST_INTERVAL_SECONDS = 6


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _call_gemini(client: genai.Client, prompt: str) -> str:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    text = response.text
    if not text:
        raise RuntimeError("Gemini API returned empty response")
    return text


def summarize_papers(
    papers: list[Paper],
    config: SummaryConfig,
) -> list[SummarizedPaper]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")

    client = genai.Client(api_key=api_key)

    summarized: list[SummarizedPaper] = []
    for i, paper in enumerate(papers):
        if i > 0:
            time.sleep(REQUEST_INTERVAL_SECONDS)

        prompt = config.prompt_template.format(
            title=paper.title,
            abstract=paper.abstract,
        )
        summary_text = _call_gemini(client, prompt)
        summarized.append(SummarizedPaper(paper=paper, summary=summary_text))

    return summarized
