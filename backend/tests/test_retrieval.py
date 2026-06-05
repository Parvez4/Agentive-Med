from app.pubmed import SEED_ARTICLES
from app.retrieval import VectorRetriever, chunk_text


def test_chunk_text_splits_long_text():
    chunks = chunk_text(" ".join(["word"] * 145), max_words=50)
    assert len(chunks) == 3


def test_retriever_returns_citations():
    retriever = VectorRetriever()
    retriever.build(SEED_ARTICLES)
    citations = retriever.search("Alzheimer caregiver nutrition")
    assert citations
    assert citations[0].pmid
    assert citations[0].url.startswith("https://pubmed.ncbi.nlm.nih.gov/")
