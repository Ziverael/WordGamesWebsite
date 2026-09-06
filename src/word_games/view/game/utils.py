from itertools import chain, zip_longest
from typing import Any

from word_games.utils import section_sort_key


class FillGapsSentences:
    @staticmethod
    def pair_responces_with_answers(response: Any, content: Any):
        correct_answers = FillGapsSentences.parse_answers(content)
        fields_no, user_answers = FillGapsSentences.parse_inputs(response)
        return {
            fields: {"expected": expected, "given": given}
            for fields, expected, given in zip_longest(
                fields_no,
                chain.from_iterable(correct_answers),
                user_answers,
                fillvalue="-",
            )
        }

    @staticmethod
    def parse_answers(
        solutions: dict[str, list[dict[str, int]]],
    ) -> list[list[str]]:
        answers: list[list[str]] = []
        for sentence, gaps in solutions.items():
            sentence_answers: list[str] = []
            for gap in gaps:
                answer = sentence[gap["start"] : gap["end"] + 1]
                answer = answer.strip()
                sentence_answers.append(answer)
            answers.append(sentence_answers)
        return answers

    @staticmethod
    def parse_inputs(inputs: dict[str, str]):
        return list(inputs.keys()), [i.strip() for i in inputs.values()]

    @staticmethod
    def grade(answers: dict[str, dict[str, str]]):
        correct = sum(v["expected"] == v["given"] for v in answers.values())
        max_points = len(answers)
        percentage_score = int(round(correct / max_points, 2) * 100)
        return correct, max_points, percentage_score

    @staticmethod
    def send_response(answers: dict[str, dict[str, str]]): ...

    @staticmethod
    def _pack_user_answers(answers: dict[str, dict[str, str]]):
        sorted_answers = sorted(
            answers.items(), key=lambda entry: section_sort_key(entry[0])
        )
        return [entry["given"] for _, entry in sorted_answers]
