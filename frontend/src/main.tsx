import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, BookOpen, Brain, CheckCircle2, Send, ShieldAlert, Stethoscope } from 'lucide-react';
import './styles.css';

type Citation = {
  pmid: string;
  title: string;
  journal: string;
  year: string;
  url: string;
  snippet: string;
  score: number;
};

type AgentTraceItem = {
  agent: string;
  action: string;
  detail: string;
};

type ChatResponse = {
  answer: string;
  citations: Citation[];
  agent_trace: AgentTraceItem[];
  safety_status: { allowed: boolean; category: string; reason: string };
  retrieval_scores: number[];
  confidence: string;
};

const examples = [
  'What are common early symptoms of Alzheimer disease?',
  'What nutrition patterns are studied for cognitive health?',
  'How can caregivers think about safety and daily routines?',
  'How much donepezil should my father take?'
];

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

function App() {
  const [question, setQuestion] = useState(examples[0]);
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function askAgentiveMed(prompt = question) {
    setQuestion(prompt);
    setLoading(true);
    setError('');
    try {
      const result = await fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: prompt })
      });
      if (!result.ok) throw new Error(`API returned ${result.status}`);
      setResponse(await result.json());
    } catch (err) {
      setResponse(buildDemoResponse(prompt));
      setError('Live backend unavailable, showing the built-in portfolio demo response.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="workspace">
        <div className="topbar">
          <div>
            <h1>Agentive Med</h1>
            <p>Multi-agent Alzheimer’s education assistant with PubMed-backed evidence.</p>
          </div>
          <div className="status"><Activity size={18} /> education-only mode</div>
        </div>

        <div className="grid">
          <section className="chatPanel">
            <div className="notice"><ShieldAlert size={18} /> Educational information only. No diagnosis, dosage, or treatment planning.</div>
            <label htmlFor="question">Ask an Alzheimer’s education question</label>
            <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} />
            <button onClick={() => askAgentiveMed()} disabled={loading}>
              <Send size={18} /> {loading ? 'Routing agents...' : 'Ask agents'}
            </button>
            {error && <div className="error">{error}</div>}
            <div className="examples">
              {examples.map((item) => (
                <button key={item} onClick={() => askAgentiveMed(item)}>{item}</button>
              ))}
            </div>
          </section>

          <section className="answerPanel">
            <div className="panelHeader">
              <Brain size={20} />
              <h2>Answer</h2>
              {response && <span className={response.safety_status.allowed ? 'badge ok' : 'badge blocked'}>{response.confidence}</span>}
            </div>
            <pre>{response ? response.answer : 'The answer will appear here with citation markers and safety status.'}</pre>
          </section>
        </div>

        <div className="detailGrid">
          <section>
            <div className="panelHeader"><Stethoscope size={20} /><h2>Agent Trace</h2></div>
            <div className="timeline">
              {(response?.agent_trace ?? []).map((item, index) => (
                <div className="trace" key={`${item.agent}-${index}`}>
                  <CheckCircle2 size={18} />
                  <div><strong>{item.agent}</strong><span>{item.action}: {item.detail}</span></div>
                </div>
              ))}
              {!response && <p className="muted">Supervisor, safety, domain, and citation verification steps will appear after a question.</p>}
            </div>
          </section>

          <section>
            <div className="panelHeader"><BookOpen size={20} /><h2>PubMed Evidence</h2></div>
            <div className="citations">
              {(response?.citations ?? []).map((citation) => (
                <a className="citation" href={citation.url} target="_blank" rel="noreferrer" key={citation.pmid}>
                  <strong>{citation.title}</strong>
                  <span>{citation.journal} · {citation.year} · PMID {citation.pmid} · score {citation.score}</span>
                  <p>{citation.snippet}</p>
                </a>
              ))}
              {response && response.citations.length === 0 && <p className="muted">{response.safety_status.reason}</p>}
              {!response && <p className="muted">Evidence cards link directly to PubMed records.</p>}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

function buildDemoResponse(prompt: string): ChatResponse {
  const blocked = /donepezil|memantine|dosage|should.*take/i.test(prompt);
  if (blocked) {
    return {
      answer: 'I can’t help with that request because the assistant cannot provide medication, dosage, or treatment instructions. I can provide general Alzheimer’s education, summarize research, or suggest questions to discuss with a licensed clinician.',
      citations: [],
      agent_trace: [
        { agent: 'Safety Guardrail Agent', action: 'evaluate', detail: 'Checked education-only boundary.' },
        { agent: 'Supervisor Agent', action: 'refuse', detail: 'Blocked category: treatment_or_dosage.' }
      ],
      safety_status: {
        allowed: false,
        category: 'treatment_or_dosage',
        reason: 'The assistant cannot provide medication, dosage, or treatment instructions.'
      },
      retrieval_scores: [],
      confidence: 'blocked'
    };
  }

  const nutrition = /nutrition|diet|eat|food|meal|mediterranean/i.test(prompt);
  return {
    answer:
      `Here is an education-only summary focused on ${nutrition ? 'nutrition and lifestyle education' : 'Alzheimer’s education'}. This is not medical advice, diagnosis, or a treatment plan.\n\n` +
      '- Alzheimer’s disease is a progressive neurodegenerative disorder and a common cause of dementia. [33740454]\n' +
      '- Mediterranean-style dietary patterns have been studied for associations with cognitive health. [29267131]\n' +
      '- Diagnosis requires professional clinical evaluation, history, cognitive assessment, and sometimes biomarker or imaging studies. [34618744]\n\n' +
      'A clinician should evaluate personal symptoms, medication questions, or care decisions.',
    citations: [
      {
        pmid: '33740454',
        title: '2021 Alzheimer’s disease facts and figures',
        journal: 'Alzheimer’s & Dementia',
        year: '2021',
        url: 'https://pubmed.ncbi.nlm.nih.gov/33740454/',
        snippet: 'Alzheimer’s disease is a progressive neurodegenerative disorder and the most common cause of dementia.',
        score: 0.84
      },
      {
        pmid: '29267131',
        title: 'Nutrition and prevention of cognitive decline',
        journal: 'Nutrients',
        year: '2018',
        url: 'https://pubmed.ncbi.nlm.nih.gov/29267131/',
        snippet: 'Dietary patterns such as Mediterranean-style diets have been studied for associations with cognitive health.',
        score: 0.79
      }
    ],
    agent_trace: [
      { agent: 'Safety Guardrail Agent', action: 'evaluate', detail: 'Checked education-only boundary.' },
      { agent: 'Supervisor Agent', action: 'route', detail: `Selected ${nutrition ? 'Nutrition Education Agent' : 'Medical Education Agent'}.` },
      { agent: nutrition ? 'Nutrition Education Agent' : 'Medical Education Agent', action: 'draft', detail: 'Generated answer from retrieved PubMed evidence.' },
      { agent: 'Citation Verifier Agent', action: 'verify', detail: 'Mapped answer to 2 retrieved citation(s).' }
    ],
    safety_status: {
      allowed: true,
      category: 'education',
      reason: 'Question is suitable for educational Alzheimer’s information.'
    },
    retrieval_scores: [0.84, 0.79],
    confidence: 'moderate'
  };
}

createRoot(document.getElementById('root')!).render(<App />);
