import json
import re
from pathlib import Path

import requests


# Configuration
API_URL = "http://127.0.0.1:8000/chat"
DATASET_PATH = Path(__file__).parent / "test_questions.json"

ABSTENTION_PHRASES = [
    "couldn't find enough information",
    "cannot find enough information",
    "not enough information",
    "not available in the documents",
    "not found in the documents",
    "don't have enough information",
    "unable to answer from the available documents",
]


def normalize(text):
    """Normalize text for simple answer matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def contains_expected_answer(answer, expected):
    """Check whether the expected answer appears in the response."""
    if not expected:
        return False

    return normalize(expected) in normalize(answer)


def extract_answer(response):
    """Extract the answer from common API response formats."""
    if isinstance(response, str):
        return response

    if isinstance(response, dict):
        for key in ("answer", "response", "message"):
            value = response.get(key)

            if isinstance(value, str):
                return value

    return ""


def extract_sources(response):
    """Extract sources from common API response formats."""
    if not isinstance(response, dict):
        return []

    for key in ("sources", "citations", "source_documents"):
        value = response.get(key)

        if isinstance(value, list):
            return value

    return []


def has_valid_source_page(sources, expected_page):
    """Check whether a source references the expected page."""
    for source in sources:
        if not isinstance(source, dict):
            continue

        page = source.get("page", source.get("page_number"))

        if page is not None:
            try:
                if int(page) == expected_page:
                    return True
            except (TypeError, ValueError):
                pass

    return False


def is_abstention(answer):
    """Check whether the bot explicitly declines to guess."""
    text = normalize(answer)

    return any(
        normalize(phrase) in text
        for phrase in ABSTENTION_PHRASES
    )

def handles_unsupported_question(answer, question):
    """
    Accept either an explicit refusal or a response that
    correctly explains the limitation of the available evidence.
    """
    text = normalize(answer)

    # A direct refusal is acceptable.
    if is_abstention(answer):
        return True

    # For the two-year warranty question, the document establishes
    # a one-year warranty, so a correction is an acceptable response.
    if "two year warranty" in normalize(question):
        mentions_one_year = (
            "one year" in text or "one year limited warranty" in text
        )

        rejects_two_year = any(
            phrase in text
            for phrase in [
                "not a two year",
                "not two year",
                "does not establish a two year",
                "does not state a two year",
                "only a one year",
                "not offer a two year",
            ]
        )

        return mentions_one_year and rejects_two_year

    return False



def main():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        questions = json.load(file)

    total = len(questions)
    answerable_total = sum(q["answerable"] for q in questions)
    unanswerable_total = total - answerable_total

    answer_correct = 0
    citation_correct = 0
    abstention_correct = 0
    api_errors = 0

    print(f"\nEvaluating {total} questions")
    print("=" * 65)

    for index, item in enumerate(questions, start=1):
        question = item["question"]

        print(f"\n[{index}/{total}] {question}")

        try:
            response = requests.post(
                API_URL,
                json={"question": question},
                timeout=90,
            )

            response.raise_for_status()
            data = response.json()

        except requests.RequestException as exc:
            print(f"API ERROR: {exc}")
            api_errors += 1
            continue

        except ValueError:
            print("API ERROR: Response was not valid JSON.")
            api_errors += 1
            continue

        answer = extract_answer(data)
        sources = extract_sources(data)

        print(f"Answer: {answer}")

        if item["answerable"]:
            correct = contains_expected_answer(
                answer,
                item["expected_answer"],
            )

            if correct:
                answer_correct += 1

            citation_ok = has_valid_source_page(
                sources,
                item["expected_page"],
            )

            if citation_ok:
                citation_correct += 1

            print(f"Answer match: {'PASS' if correct else 'FAIL'}")
            print(
                f"Expected page citation: "
                f"{'PASS' if citation_ok else 'FAIL'}"
            )
        

        else:
            handled_correctly = handles_unsupported_question(
                answer,
                question,
            )

            if handled_correctly:
                abstention_correct += 1

            print(
                f"Unsupported-question handling: "
                f"{'PASS' if handled_correctly else 'FAIL'}"
            )

        if not sources:
            print("Warning: No sources returned by the API.")

    print("\n" + "=" * 65)
    print("EVALUATION SUMMARY")
    print("=" * 65)

    print(f"Total questions: {total}")
    print(f"Answerable questions: {answerable_total}")
    print(f"Unanswerable questions: {unanswerable_total}")
    print(f"API errors: {api_errors}")

    if answerable_total:
        print(
            f"Answer match rate: "
            f"{answer_correct}/{answerable_total} "
            f"({answer_correct / answerable_total:.1%})"
        )

        print(
            f"Expected page citation rate: "
            f"{citation_correct}/{answerable_total} "
            f"({citation_correct / answerable_total:.1%})"
        )

    if unanswerable_total:
        print(
            f"Abstention rate: "
            f"{abstention_correct}/{unanswerable_total} "
            f"({abstention_correct / unanswerable_total:.1%})"
        )


if __name__ == "__main__":
    main()