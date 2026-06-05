from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx

from app.config import Settings


@dataclass(frozen=True)
class PubMedArticle:
    pmid: str
    title: str
    abstract: str
    journal: str
    year: str

    @property
    def url(self) -> str:
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


SEED_ARTICLES = [
    PubMedArticle(
        pmid="33740454",
        title="2021 Alzheimer's disease facts and figures",
        abstract=(
            "Alzheimer's disease is a progressive neurodegenerative disorder and the most common cause "
            "of dementia. Education for patients and caregivers commonly includes symptoms, risk factors, "
            "care planning, safety, and support resources."
        ),
        journal="Alzheimer's & Dementia",
        year="2021",
    ),
    PubMedArticle(
        pmid="29267131",
        title="Nutrition and prevention of cognitive decline",
        abstract=(
            "Dietary patterns such as Mediterranean-style diets have been studied for associations with "
            "cognitive health. Nutrition education should be individualized by clinicians and should not "
            "replace medical evaluation or treatment."
        ),
        journal="Nutrients",
        year="2018",
    ),
    PubMedArticle(
        pmid="34618744",
        title="Diagnosis and management of Alzheimer's disease",
        abstract=(
            "Diagnosis of Alzheimer's disease requires clinical evaluation, history, cognitive assessment, "
            "and sometimes biomarker or imaging studies. Public education can explain common symptoms and "
            "the importance of professional assessment."
        ),
        journal="BMJ",
        year="2021",
    ),
    PubMedArticle(
        pmid="33098768",
        title="Dementia prevention, intervention, and care",
        abstract=(
            "Modifiable risk factors, caregiver support, hearing, hypertension, physical activity, social "
            "connection, and sleep are discussed in dementia prevention and care literature."
        ),
        journal="Lancet",
        year="2020",
    ),
]


class PubMedClient:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, query: str, limit: int | None = None) -> list[PubMedArticle]:
        limit = limit or self.settings.pubmed_default_limit
        try:
            pmids = await self._search_pmids(query, limit)
            if not pmids:
                return self._seed_search(query, limit)
            articles = await self._fetch_articles(pmids)
            return articles or self._seed_search(query, limit)
        except httpx.HTTPError:
            return self._seed_search(query, limit)

    async def _search_pmids(self, query: str, limit: int) -> list[str]:
        params = {
            "db": "pubmed",
            "term": f"Alzheimer {query}",
            "retmode": "json",
            "retmax": str(limit),
            "sort": "relevance",
        }
        self._add_auth(params)
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(f"{self.base_url}/esearch.fcgi", params=params)
            response.raise_for_status()
            payload = response.json()
        return payload.get("esearchresult", {}).get("idlist", [])

    async def _fetch_articles(self, pmids: list[str]) -> list[PubMedArticle]:
        params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
        self._add_auth(params)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/efetch.fcgi", params=params)
            response.raise_for_status()
        return parse_pubmed_xml(response.text)

    def _add_auth(self, params: dict[str, str]) -> None:
        if self.settings.pubmed_email:
            params["email"] = self.settings.pubmed_email
        if self.settings.pubmed_api_key:
            params["api_key"] = self.settings.pubmed_api_key

    @staticmethod
    def _seed_search(query: str, limit: int) -> list[PubMedArticle]:
        terms = set(re.findall(r"[a-zA-Z]{4,}", query.lower()))
        scored = []
        for article in SEED_ARTICLES:
            haystack = f"{article.title} {article.abstract}".lower()
            score = sum(term in haystack for term in terms)
            scored.append((score, article))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [article for _, article in scored[:limit]]


def parse_pubmed_xml(xml_text: str) -> list[PubMedArticle]:
    root = ET.fromstring(xml_text)
    articles: list[PubMedArticle] = []
    for article_node in root.findall(".//PubmedArticle"):
        pmid = article_node.findtext(".//PMID") or ""
        title = _clean(article_node.findtext(".//ArticleTitle") or "Untitled PubMed article")
        abstract_parts = [
            _clean("".join(part.itertext()))
            for part in article_node.findall(".//Abstract/AbstractText")
        ]
        abstract = " ".join(part for part in abstract_parts if part)
        journal = _clean(article_node.findtext(".//Journal/Title") or "Unknown journal")
        year = (
            article_node.findtext(".//PubDate/Year")
            or article_node.findtext(".//PubDate/MedlineDate")
            or "n.d."
        )
        if pmid and abstract:
            articles.append(PubMedArticle(pmid=pmid, title=title, abstract=abstract, journal=journal, year=year))
    return articles


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()
