import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell} from 'recharts';
import {Send, Database, FileText} from 'lucide-react';
import {ask, topTitles, cityEngagement} from './api/client';
import './styles.css';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const examples = [
  'Which titles performed best in 2025?',
  'Why is Stellar Run trending recently?',
  'Compare Dark Orbit vs Last Kingdom.',
  'Which city had the strongest engagement last month?',
  'What explains weak comedy performance?',
  'What recommendations would you give for leadership?'
];

// Subtle indigo bar colors
const BAR_COLOR = '#6366f1';

function App() {
  const [question, setQuestion] = useState(examples[0]);
  const [messages, setMessages] = useState([]);
  const [trace, setTrace] = useState([]);
  const [chart, setChart] = useState([]);
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [backendReady, setBackendReady] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        const [titles, cityData] = await Promise.all([topTitles(), cityEngagement()]);
        setChart(titles);
        setCities(cityData);
        setBackendReady(true);
      } catch (err) {
        console.error(err);
        setTimeout(init, 2000);
      }
    }
    init();
  }, []);

  async function submit(q = question) {
    if (!q.trim()) return;
    setLoading(true);
    setMessages(m => [...m, {role: 'user', content: q}]);
    try {
      const res = await ask(q);
      setMessages(m => [...m, {role: 'assistant', content: res.answer, sources: res.sources}]);
      setTrace(res.tool_trace || []);
    } catch (e) {
      setMessages(m => [...m, {role: 'assistant', content: `Error: ${e.message}`}]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      {!backendReady && (
        <div className="overlay">
          <div className="overlay-box">
            <div className="spinner" />
            <p>Waking up server…</p>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <aside className="sidebar">
        <h1>Secure AI Insights</h1>
        <p className="muted">
          Secure, context-aware AI across your entire data landscape.
        </p>
        <h3>Example questions</h3>
        {examples.map(e => (
          <button className="example" key={e} onClick={() => { setQuestion(e); submit(e); }}>
            {e}
          </button>
        ))}
      </aside>

      {/* Main content */}
      <main>
        <section className="grid">
          <div className="card wide">
            <h2>Top titles by views</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chart} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="title"
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                  angle={-12}
                  textAnchor="end"
                  height={52}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                  width={1}
                />
                <Tooltip
                  contentStyle={{
                    border: '0.5px solid #e2e8f0',
                    borderRadius: 10,
                    fontSize: 12.5,
                    boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
                  }}
                  cursor={{ fill: 'rgba(99,102,241,0.06)' }}
                />
                <Bar dataKey="total_views" fill={BAR_COLOR} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h2>City engagement</h2>
            {cities.slice(0, 5).map(c => (
              <div className="row" key={c.city}>
                <span>{c.city}</span>
                <b>{c.avg_engagement}</b>
              </div>
            ))}
          </div>
        </section>

        <section className="chat card">
          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <b>{m.role === 'user' ? 'You' : 'Assistant'}</b>
                {m.role === 'assistant' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                ) : (
                  <p>{m.content}</p>
                )}
                {m.sources && (
                  <small>
                    Sources: SQL {m.sources.sql_queries?.join(', ')}
                    {m.sources.documents?.length ? ` · PDFs: ${m.sources.documents.map(d => d.source).join(', ')}` : ''}
                  </small>
                )}
              </div>
            ))}
            {loading && <p className="muted">Thinking…</p>}
          </div>

          <div className="composer">
            <input
              value={question}
              placeholder="Ask anything about your data…"
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') submit(); }}
            />
            <button onClick={() => submit()}>
              <Send size={14} /> Ask
            </button>
          </div>
        </section>
      </main>

      {/* Trace sidebar */}
      <aside className="trace">
        <h2>Tool trace</h2>
        {trace.map((t, i) => (
          <div className="traceitem" key={i}>
            {t.tool === 'document_retrieval' ? <FileText size={14} /> : <Database size={14} />}
            <span>{t.tool}</span>
            <small>{t.input} · {t.rows} rows</small>
          </div>
        ))}
      </aside>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);