const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
const roleHeaders = { 'Content-Type': 'application/json', 'x-user-role': 'leadership' };
export async function ask(question){const r=await fetch(`${API_BASE}/chat`,{method:'POST',headers:roleHeaders,body:JSON.stringify({question})}); if(!r.ok) throw new Error(await r.text()); return r.json();}
export async function topTitles(){const r=await fetch(`${API_BASE}/analytics/top-titles`,{headers:roleHeaders}); return (await r.json()).rows;}
export async function cityEngagement(){const r=await fetch(`${API_BASE}/analytics/city-engagement`,{headers:roleHeaders}); return (await r.json()).rows;}
