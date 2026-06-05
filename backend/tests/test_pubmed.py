from app.pubmed import parse_pubmed_xml


def test_parse_pubmed_xml_extracts_article():
    xml = """
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <PMID>123</PMID>
          <Article>
            <Journal><Title>Test Journal</Title><JournalIssue><PubDate><Year>2026</Year></PubDate></JournalIssue></Journal>
            <ArticleTitle>Alzheimer test title</ArticleTitle>
            <Abstract><AbstractText>Evidence text.</AbstractText></Abstract>
          </Article>
        </MedlineCitation>
      </PubmedArticle>
    </PubmedArticleSet>
    """
    articles = parse_pubmed_xml(xml)
    assert len(articles) == 1
    assert articles[0].pmid == "123"
    assert articles[0].abstract == "Evidence text."
