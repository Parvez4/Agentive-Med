from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import AgentTraceItem, ChatResponse, Citation, SafetyStatus
from app.safety import SafetyGuardrail


NUTRITION_TERMS = {
    "diet",
    "eat",
    "eating",
    "food",
    "meal",
    "mediterranean",
    "nutrition",
    "exercise",
    "lifestyle",
}


@dataclass
class AgentiveMedOrchestrator:
    safety: SafetyGuardrail

    def answer(self, question: str, citations: list[Citation]) -> ChatResponse:
        trace = [
            AgentTraceItem(agent="Safety Guardrail Agent", action="evaluate", detail="Checked education-only boundary."),
        ]
        safety_status = self.safety.evaluate(question)
        if not safety_status.allowed:
            trace.append(
                AgentTraceItem(agent="Supervisor Agent", action="refuse", detail=f"Blocked category: {safety_status.category}.")
            )
            return ChatResponse(
                answer=self._safe_refusal(safety_status),
                citations=[],
                agent_trace=trace,
                safety_status=safety_status,
                retrieval_scores=[],
                confidence="blocked",
            )

        route = self._route(question)
        trace.append(AgentTraceItem(agent="Supervisor Agent", action="route", detail=f"Selected {route}."))
        trace.append(AgentTraceItem(agent=route, action="draft", detail="Generated answer from retrieved PubMed evidence."))
        trace.append(
            AgentTraceItem(
                agent="Citation Verifier Agent",
                action="verify",
                detail=f"Mapped answer to {len(citations)} retrieved citation(s).",
            )
        )
        return ChatResponse(
            answer=self._compose_answer(question, route, citations),
            citations=citations,
            agent_trace=trace,
            safety_status=safety_status,
            retrieval_scores=[citation.score for citation in citations],
            confidence=self._confidence(citations),
        )

    @staticmethod
    def _route(question: str) -> str:
        tokens = set(re.findall(r"[a-zA-Z]+", question.lower()))
        if tokens & NUTRITION_TERMS:
            return "Nutrition Education Agent"
        return "Medical Education Agent"

    @staticmethod
    def _compose_answer(question: str, route: str, citations: list[Citation]) -> str:
        if not citations:
            return (
                "I could not retrieve enough PubMed evidence to answer confidently. "
                "For Alzheimer’s education, consider asking about symptoms, risk factors, caregiving support, "
                "or the role of professional evaluation."
            )
        evidence = citations[:3]
        focus = "nutrition and lifestyle education" if route.startswith("Nutrition") else "Alzheimer’s education"
        bullets = []
        for citation in evidence:
            snippet = citation.snippet.rstrip(".")
            bullets.append(f"- {snippet}. [{citation.pmid}]")
        return (
            f"Here is an education-only summary focused on {focus}. This is not medical advice, diagnosis, "
            f"or a treatment plan.\n\n"
            + "\n".join(bullets)
            + "\n\nA clinician should evaluate personal symptoms, medication questions, or care decisions."
        )

    @staticmethod
    def _safe_refusal(status: SafetyStatus) -> str:
        if status.category == "emergency":
            return (
                "I cannot handle emergency or crisis situations. Please call emergency services immediately "
                "or contact a local crisis line. I can only provide general Alzheimer’s education."
            )
        return (
            f"I can’t help with that request because: {status.reason} "
            "I can provide general Alzheimer’s education, explain common symptoms, summarize research, "
            "or suggest questions to discuss with a licensed clinician."
        )

    @staticmethod
    def _confidence(citations: list[Citation]) -> str:
        if len(citations) >= 3 and max(c.score for c in citations) > 0.2:
            return "moderate"
        if citations:
            return "low"
        return "insufficient"
