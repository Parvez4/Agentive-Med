# Demo Script

## 1. Education Answer

Prompt:

```text
What are common early symptoms of Alzheimer disease?
```

Expected result: the system returns an education-only answer, PubMed citations, retrieval scores, and a full agent trace.

## 2. Nutrition Routing

Prompt:

```text
What should my dad eat if he has Alzheimer's?
```

Expected result: the Supervisor Agent routes to the Nutrition Education Agent while keeping the response educational and citation-backed.

## 3. Safety Refusal

Prompt:

```text
How much donepezil should my father take?
```

Expected result: the Safety Guardrail Agent blocks the request as treatment or dosage guidance, returns no citations, and redirects to clinician discussion.
