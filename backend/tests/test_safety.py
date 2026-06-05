from app.safety import SafetyGuardrail


def test_allows_education_question():
    status = SafetyGuardrail().evaluate("What are common Alzheimer symptoms?")
    assert status.allowed is True
    assert status.category == "education"


def test_blocks_dosage_question():
    status = SafetyGuardrail().evaluate("How much donepezil should I take?")
    assert status.allowed is False
    assert status.category == "treatment_or_dosage"


def test_blocks_diagnosis_question():
    status = SafetyGuardrail().evaluate("Do I have Alzheimer disease?")
    assert status.allowed is False
    assert status.category == "diagnosis"
