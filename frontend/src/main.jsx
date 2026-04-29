import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid} from 'recharts';
import {Send, ShieldCheck, Database, FileText} from 'lucide-react';
import {ask, topTitles, cityEngagement} from './api/client';
import './styles.css';

const examples = [
  'Which titles performed best in 2025?',
  'Why is Stellar Run trending recently?',
  'Compare Dark Orbit vs Last Kingdom.',
  'Which city had the strongest engagement last month?',
  'What explains weak comedy performance?',
  'What recommendations would you give for leadership?'
];

function App(){
  const [question,setQuestion]=useState(examples[0]);
  const [messages,setMessages]=useState([]);
  const [trace,setTrace]=useState([]);
  const [chart,setChart]=useState([]);
  const [cities,setCities]=useState([]);
  const [loading,setLoading]=useState(false);

  useEffect(()=>{topTitles().then(setChart).catch(console.error); cityEngagement().then(setCities).catch(console.error);},[]);
  async function submit(q=question){
    if(!q.trim()) return;
    setLoading(true); setMessages(m=>[...m,{role:'user',content:q}]);
    try{const res=await ask(q); setMessages(m=>[...m,{role:'assistant',content:res.answer,sources:res.sources}]); setTrace(res.tool_trace||[]);}
    catch(e){setMessages(m=>[...m,{role:'assistant',content:`Error: ${e.message}`}]);}
    finally{setLoading(false);}
  }
  return <div className="app">
    <aside className="sidebar">
      <h1>Secure AI Insights</h1>
      <p className="muted">Multi-source analytics assistant with tool-based access, role checks, SQL safety, and PDF retrieval.</p>
      <div className="badge"><ShieldCheck size={16}/> leadership role</div>
      <h3>Example questions</h3>
      {examples.map(e=><button className="example" key={e} onClick={()=>{setQuestion(e); submit(e)}}>{e}</button>)}
    </aside>
    <main>
      <section className="grid">
        <div className="card wide"><h2>Top Titles by Views</h2><ResponsiveContainer width="100%" height={260}><BarChart data={chart}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="title" angle={-15} textAnchor="end" height={70}/><YAxis/><Tooltip/><Bar dataKey="total_views"/></BarChart></ResponsiveContainer></div>
        <div className="card"><h2>City Engagement</h2>{cities.slice(0,5).map(c=><div className="row" key={c.city}><span>{c.city}</span><b>{c.avg_engagement}</b></div>)}</div>
      </section>
      <section className="chat card">
        <div className="messages">{messages.map((m,i)=><div key={i} className={`msg ${m.role}`}><b>{m.role==='user'?'You':'Assistant'}</b><p>{m.content}</p>{m.sources&&<small>Sources: SQL queries {m.sources.sql_queries?.join(', ')}; PDFs {m.sources.documents?.map(d=>d.source).join(', ')}</small>}</div>)}{loading&&<p className="muted">Thinking with approved tools...</p>}</div>
        <div className="composer"><input value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')submit()}}/><button onClick={()=>submit()}><Send size={16}/> Ask</button></div>
      </section>
    </main>
    <aside className="trace"><h2>Tool Trace</h2>{trace.map((t,i)=><div className="traceitem" key={i}>{t.tool==='document_retrieval'?<FileText size={15}/>:<Database size={15}/>}<span>{t.tool}</span><small>{t.input} · {t.rows} rows</small></div>)}</aside>
  </div>
}

createRoot(document.getElementById('root')).render(<App/>);
