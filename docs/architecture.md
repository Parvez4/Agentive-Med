# Agentive Med Architecture

Agentive Med uses a FastAPI backend as the orchestration boundary and a React UI as the demo surface.

## Request Flow

1. The UI posts a user question to `POST /chat`.
2. The Safety Guardrail Agent classifies the prompt as education, diagnosis, treatment/dosage, or emergency.
3. Allowed education prompts query PubMed through NCBI E-utilities.
4. Abstracts are chunked, embedded with a deterministic local embedding function, and ranked with FAISS when available.
5. The Supervisor Agent routes to the Medical Education Agent or Nutrition Education Agent.
6. The Citation Verifier Agent attaches citation evidence and retrieval scores to the final response.

## Production Upgrade Path

- Replace deterministic answer drafting with AG2 `ConversableAgent` calls using the OpenAI-compatible settings in `.env`.
- Persist FAISS indexes and citation metadata under `data/`.
- Add auth, rate limiting, request IDs, and OpenTelemetry tracing before public deployment.
- Add a curated Alzheimer’s evaluation set with clinician-reviewed expected refusal and citation behavior.
