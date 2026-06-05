import re

from app.models import SafetyStatus


DIAGNOSIS_PATTERNS = [
    r"\bdo i have\b",
    r"\bdiagnos(e|is|ed)\b",
    r"\bwhat stage\b",
    r"\bconfirm.*alzheimer",
]
TREATMENT_PATTERNS = [
    r"\bdosage\b",
    r"\bhow much (donepezil|memantine|medicine|medication)\b",
    r"\bshould i take\b",
    r"\bprescrib(e|ed|ing)\b",
    r"\bstop taking\b",
]
EMERGENCY_PATTERNS = [
    r"\bsuicid(e|al)\b",
    r"\bchest pain\b",
    r"\bcan't breathe\b",
    r"\bunconscious\b",
    r"\bemergency\b",
]


class SafetyGuardrail:
    def evaluate(self, question: str) -> SafetyStatus:
        text = question.lower()
        if self._matches(text, EMERGENCY_PATTERNS):
            return SafetyStatus(
                allowed=False,
                category="emergency",
                reason="Emergency or crisis language requires immediate professional help.",
            )
        if self._matches(text, TREATMENT_PATTERNS):
            return SafetyStatus(
                allowed=False,
                category="treatment_or_dosage",
                reason="The assistant cannot provide medication, dosage, or treatment instructions.",
            )
        if self._matches(text, DIAGNOSIS_PATTERNS):
            return SafetyStatus(
                allowed=False,
                category="diagnosis",
                reason="The assistant cannot diagnose Alzheimer’s disease or assess an individual patient.",
            )
        return SafetyStatus(
            allowed=True,
            category="education",
            reason="Question is suitable for educational Alzheimer’s information.",
        )

    @staticmethod
    def _matches(text: str, patterns: list[str]) -> bool:
        return any(re.search(pattern, text) for pattern in patterns)
