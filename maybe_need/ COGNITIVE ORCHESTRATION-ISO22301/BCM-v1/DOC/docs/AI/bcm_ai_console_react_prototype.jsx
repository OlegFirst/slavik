import React, { useMemo, useState, useEffect } from "react";

// BCM AI Console — single-file React prototype
// TailwindCSS styling (no imports required in canvas)
// Notes:
// - Left sidebar: modules
// - Top bar: org/client selector, search, quick actions
// - Main: widgets switch by module
// - Right drawer: AI panel (context-aware suggestions, draft actions)
// - Bottom: event log (simulated)

const modules = [
  { key: "overview", label: "Overview", emoji: "🏠" },
  { key: "bia", label: "BIA", emoji: "📐" },
  { key: "plans", label: "BCP/DRP", emoji: "📄" },
  { key: "incidents", label: "Incidents", emoji: "🚨" },
  { key: "exercises", label: "Exercises", emoji: "🎯" },
  { key: "audit", label: "Audit", emoji: "🧾" },
  { key: "kpi", label: "KPI", emoji: "📊" },
  { key: "community", label: "Scenario Hub", emoji: "🌐" },
  { key: "users", label: "Users", emoji: "👥" },
  { key: "orchestrator", label: "Orchestrator", emoji: "🤖" },
];

const mockClients = [
  { id: "hosp-01", name: "St. Mark Hospital" },
  { id: "lab-02", name: "BetterLab Diagnostics" },
  { id: "moh-01", name: "Public Health Dept." },
];

const Pill = ({ color = "bg-emerald-500", text = "OK" }) => (
  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium text-white ${color}`}>{text}</span>
);

const Card = ({ title, children, right }) => (
  <div className="bg-white/80 backdrop-blur border border-slate-200 rounded-2xl p-4 shadow-sm">
    <div className="flex items-center justify-between mb-3">
      <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      <div>{right}</div>
    </div>
    {children}
  </div>
);

function Gauge({ value = 78 }) {
  // simple donut gauge
  const r = 36;
  const c = 2 * Math.PI * r;
  const clamped = Math.max(0, Math.min(100, value));
  const dash = (clamped / 100) * c;
  return (
    <svg viewBox="0 0 100 100" className="w-24 h-24">
      <circle cx="50" cy="50" r={r} stroke="#e5e7eb" strokeWidth="10" fill="none" />
      <circle cx="50" cy="50" r={r} stroke="#10b981" strokeWidth="10" fill="none" strokeLinecap="round" strokeDasharray={`${dash} ${c}`} transform="rotate(-90 50 50)" />
      <text x="50" y="53" textAnchor="middle" className="fill-slate-800 text-lg font-bold">{clamped}%</text>
    </svg>
  );
}

function ProgressBar({ value }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
      <div className="h-full bg-indigo-500" style={{ width: `${v}%` }} />
    </div>
  );
}

function Table({ columns, rows }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500">
            {columns.map((c) => (
              <th key={c.key} className="px-3 py-2 font-medium">{c.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, idx) => (
            <tr key={idx} className="border-t border-slate-100">
              {columns.map((c) => (
                <td key={c.key} className="px-3 py-2 text-slate-800">{c.render ? c.render(r[c.key], r) : r[c.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const nowIso = () => new Date().toISOString().slice(0, 19).replace("T", " ");

export default function BcmAiConsole() {
  const [active, setActive] = useState("overview");
  const [client, setClient] = useState(mockClients[0].id);
  const [query, setQuery] = useState("");
  const [aiOpen, setAiOpen] = useState(true);
  const [events, setEvents] = useState([
    { t: nowIso(), msg: "bcm.context.updated — 12 processes imported", lvl: "info" },
    { t: nowIso(), msg: "bcm.bia.completed — High: 5, Med: 11", lvl: "info" },
  ]);
  const clientName = useMemo(() => mockClients.find((c) => c.id === client)?.name || client, [client]);

  // Mock AI conversation
  const [aiMsgs, setAiMsgs] = useState([
    { role: "system", text: "AI Orchestrator online. Ask me anything about BCM status." },
    { role: "assistant", text: "I see 2 open CAPA items and one plan older than 180 days." },
  ]);
  const [aiInput, setAiInput] = useState("");

  function pushEvent(msg, lvl = "info") {
    setEvents((e) => [{ t: nowIso(), msg, lvl }, ...e.slice(0, 49)]);
  }

  function sendAi() {
    if (!aiInput.trim()) return;
    const q = aiInput.trim();
    setAiMsgs((m) => [...m, { role: "user", text: q }]);
    // naive mock routing
    let reply = "";
    if (/generate.*bcp/i.test(q)) {
      reply = "Draft BCP ready: 8 steps, 2 comms, 3 resources. Push to Plans?";
    } else if (/tabletop|exercise|учени/i.test(q)) {
      reply = "Recommended scenario: Cyber EHR outage (tabletop, 45 min). Start now?";
    } else if (/kpi|risk|риск/i.test(q)) {
      reply = "KPI summary: BIA 86% \u2191, Plans up-to-date 72% \u2193, CAPA on-time 81% \u2191.";
    } else {
      reply = `I can draft plans, propose exercises, summarize audits, or explain RTO/RPO. Context: ${clientName}`;
    }
    setTimeout(() => setAiMsgs((m) => [...m, { role: "assistant", text: reply }]), 400);
    setAiInput("");
  }

  // Widgets per module
  const content = useMemo(() => {
    switch (active) {
      case "overview":
        return (
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
            <Card title="AI Health Score" right={<Pill text="stable" /> }>
              <div className="flex items-center gap-6">
                <Gauge value={78} />
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2"><Pill color="bg-emerald-500" text="BIA 86%" /> Coverage</div>
                  <div className="flex items-center gap-2"><Pill color="bg-amber-500" text="Plans 72%" /> Up-to-date</div>
                  <div className="flex items-center gap-2"><Pill color="bg-sky-500" text="CAPA 81%" /> On time</div>
                </div>
              </div>
            </Card>
            <div className="xl:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card title="PDCA Wheel" right={<span className="text-xs text-slate-500">live</span>}>
                <div className="flex flex-wrap gap-2 text-xs">
                  {"Context → BIA → Plans → Training → Incidents → Exercises → Audit → KPI → MR"}
                </div>
                <div className="mt-3 text-xs text-slate-500">Next action: Schedule tabletops for 2 High processes (overdue 37d).</div>
              </Card>
              <Card title="Open Alerts">
                <ul className="text-sm space-y-1">
                  <li>⚠️ EHR RTO exceeds target by 2h</li>
                  <li>⚠️ Pharmacy generator test overdue (12d)</li>
                  <li>ℹ️ New scenario published: Supply chain disruption</li>
                </ul>
              </Card>
              <Card title="Training Progress">
                <div className="space-y-2">
                  <div className="flex items-center justify-between"><span>Nursing</span><span>92%</span></div>
                  <ProgressBar value={92} />
                  <div className="flex items-center justify-between"><span>IT</span><span>88%</span></div>
                  <ProgressBar value={88} />
                  <div className="flex items-center justify-between"><span>Admin</span><span>76%</span></div>
                  <ProgressBar value={76} />
                </div>
              </Card>
              <Card title="Upcoming Reviews">
                <ul className="text-sm space-y-1">
                  <li>MR Q3 • Sep 10 • Owner: COO</li>
                  <li>BCP: Laboratory • Review due Sep 05</li>
                  <li>Audit: ISO 22301 internal • Sep 18</li>
                </ul>
              </Card>
            </div>
            <div className="xl:col-span-5">
              <Card title="Recent Events">
                <div className="max-h-64 overflow-auto divide-y divide-slate-100">
                  {events.map((e, i) => (
                    <div key={i} className="py-2 flex items-start gap-3 text-sm">
                      <span className="text-slate-400 shrink-0 w-28">{e.t}</span>
                      <span className="text-slate-700">{e.msg}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        );
      case "bia":
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card title="Critical Processes (High)">
              <Table columns={[
                { key: "proc", title: "Process" },
                { key: "rto", title: "RTO" },
                { key: "rpo", title: "RPO" },
                { key: "mtpd", title: "MTPD" },
              ]} rows={[
                { proc: "EHR", rto: "4h", rpo: "1h", mtpd: "24h" },
                { proc: "Pharmacy", rto: "8h", rpo: "2h", mtpd: "48h" },
                { proc: "Lab", rto: "6h", rpo: "2h", mtpd: "36h" },
              ]} />
            </Card>
            <Card title="Actions" right={<Pill color="bg-indigo-500" text="AI"/>}>
              <div className="text-sm space-y-2">
                <button onClick={() => {pushEvent("/compute sent for 3 processes");}} className="px-3 py-2 bg-slate-900 text-white rounded-lg text-xs">Recompute BIA</button>
                <button onClick={() => {pushEvent("Draft BCP requested (EHR)"); setActive("plans");}} className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-xs">Generate BCP draft (EHR)</button>
              </div>
            </Card>
          </div>
        );
      case "plans":
        return (
          <div className="grid grid-cols-1 gap-4">
            <Card title="Plans">
              <Table columns={[
                { key: "name", title: "Plan" },
                { key: "ver", title: "Version" },
                { key: "age", title: "Age" },
                { key: "status", title: "Status", render: (v) => <Pill color={v === "Published" ? "bg-emerald-500" : "bg-amber-500"} text={v}/> },
              ]} rows={[
                { name: "BCP — EHR", ver: "v3", age: "189d", status: "Draft" },
                { name: "BCP — Pharmacy", ver: "v5", age: "45d", status: "Published" },
              ]} />
            </Card>
            <div className="flex gap-2">
              <button onClick={() => pushEvent("Plan v4 (EHR) published")} className="px-3 py-2 bg-emerald-600 text-white rounded-lg text-xs">Publish Draft</button>
              <button onClick={() => pushEvent("Sent for approval: BCP EHR v4")} className="px-3 py-2 bg-slate-900 text-white rounded-lg text-xs">Send for Approval</button>
            </div>
          </div>
        );
      case "incidents":
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card title="Open Incidents">
              <Table columns={[{key:"id",title:"Case"},{key:"sev",title:"Sev"},{key:"owner",title:"Owner"},{key:"eta",title:"ETA"}]}
                rows={[{id:"TH-9321",sev:"High",owner:"IR Team",eta:"2h"},{id:"TH-9344",sev:"Med",owner:"IT",eta:"5h"}]} />
            </Card>
            <Card title="Playbook" right={<Pill color="bg-indigo-500" text="AI"/>}>
              <div className="text-sm space-y-2">
                <button onClick={()=>pushEvent("AI suggested response draft for TH-9321")}
                  className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-xs">Suggest response draft</button>
                <button onClick={()=>pushEvent("Comms brief generated for TH-9321")}
                  className="px-3 py-2 bg-slate-900 text-white rounded-lg text-xs">Generate comms brief</button>
              </div>
            </Card>
            <Card title="Timeline">
              <ul className="text-sm space-y-1">
                <li>12:01 TH-9321 detected</li>
                <li>12:07 Owner assigned (IR)</li>
                <li>12:20 AI draft produced</li>
              </ul>
            </Card>
          </div>
        );
      case "exercises":
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card title="Scenario Hub">
              <Table columns={[{key:"title",title:"Scenario"},{key:"type",title:"Type"},{key:"rating",title:"Rating"}]}
                rows={[{title:"Cyber EHR outage",type:"Tabletop",rating:"4.6"},{title:"Blackout campus-wide",type:"Full",rating:"4.3"}]} />
            </Card>
            <Card title="Run Exercise" right={<Pill color="bg-indigo-500" text="AI"/>}>
              <div className="text-sm space-y-2">
                <button onClick={()=>pushEvent("Exercise started: Cyber EHR outage")}
                  className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-xs">Start tabletop</button>
                <button onClick={()=>pushEvent("Simulation queued (Blackout)")}
                  className="px-3 py-2 bg-slate-900 text-white rounded-lg text-xs">Run simulation</button>
              </div>
            </Card>
          </div>
        );
      case "audit":
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card title="ISO 22301 Checklist">
              <Table columns={[{key:"cl",title:"Clause"},{key:"score",title:"Score"},{key:"evidence",title:"Evidence"}]}
                rows={[{cl:"8.2 BIA",score:"✔",evidence:"bia_2025q3.pdf"},{cl:"8.4 Plans",score:"~",evidence:"bcp_ehr_v3.docx"}]} />
            </Card>
            <Card title="Evidence" right={<Pill color="bg-indigo-500" text="AI"/>}>
              <div className="text-sm space-y-2">
                <button onClick={()=>pushEvent("Evidence summarized for 8.4")}
                  className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-xs">Summarize evidence</button>
                <button onClick={()=>pushEvent("CAPA created: Communication drill")}
                  className="px-3 py-2 bg-emerald-600 text-white rounded-lg text-xs">Create CAPA</button>
              </div>
            </Card>
            <Card title="Findings">
              <ul className="text-sm space-y-1">
                <li>Gap: BCP EHR outdated (189d)</li>
                <li>Gap: Generator test missing logs</li>
              </ul>
            </Card>
          </div>
        );
      case "kpi":
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card title="Coverage">
              <div className="text-sm space-y-2">
                <div className="flex items-center justify-between"><span>BIA</span><span>86%</span></div>
                <ProgressBar value={86} />
                <div className="flex items-center justify-between"><span>Plans up-to-date</span><span>72%</span></div>
                <ProgressBar value={72} />
                <div className="flex items-center justify-between"><span>Training</span><span>85%</span></div>
                <ProgressBar value={85} />
              </div>
            </Card>
            <Card title="Incidents SLA">
              <div className="text-sm space-y-2">
                <div className="flex items-center justify-between"><span>Closed in SLA</span><span>91%</span></div>
                <ProgressBar value={91} />
                <div className="flex items-center justify-between"><span>Avg TTR</span><span>2.1h</span></div>
              </div>
            </Card>
            <Card title="CAPA">
              <div className="text-sm space-y-2">
                <div className="flex items-center justify-between"><span>On-time</span><span>81%</span></div>
                <ProgressBar value={81} />
                <div className="flex items-center justify-between"><span>Overdue</span><span>3</span></div>
              </div>
            </Card>
          </div>
        );
      case "community":
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card title="Published Scenarios">
              <Table columns={[{key:"title",title:"Title"},{key:"owner",title:"Owner"},{key:"rating",title:"★"}]}
                rows={[{title:"EHR Ransomware",owner:"@auditor_alex",rating:"4.8"},{title:"Oxygen outage",owner:"@ops_irina",rating:"4.6"}]} />
            </Card>
            <Card title="Submit New Scenario" right={<Pill color="bg-indigo-500" text="AI"/>}>
              <div className="text-sm space-y-2">
                <button onClick={()=>pushEvent("Scenario draft generated: Supply Chain (tabletop)")}
                  className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-xs">AI generate draft</button>
                <button onClick={()=>pushEvent("Scenario submitted for review")}
                  className="px-3 py-2 bg-emerald-600 text-white rounded-lg text-xs">Submit for review</button>
              </div>
            </Card>
          </div>
        );
      case "users":
        return (
          <Card title="Users & Roles">
            <Table columns={[{key:"user",title:"User"},{key:"role",title:"Role"},{key:"company",title:"Company"}]}
              rows={[{user:"sara@mark.org",role:"ClientAdmin",company:"St. Mark Hospital"},{user:"audit@qa.org",role:"Auditor",company:"Public Health Dept."}]} />
          </Card>
        );
      case "orchestrator":
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card title="Recent Events (webhooks)">
              <ul className="text-sm space-y-1">
                <li>bcm.bia.completed → Gen BCP draft (EHR)</li>
                <li>bcm.incident.opened → Response draft (TH-9321)</li>
              </ul>
            </Card>
            <Card title="Rules">
              <ul className="text-sm space-y-1">
                <li>High & plan_age&gt;180d → schedule tabletop</li>
                <li>Incident sev=High → comms brief + response steps</li>
              </ul>
            </Card>
          </div>
        );
      default:
        return null;
    }
  }, [active, events, clientName]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Top bar */}
      <div className="sticky top-0 z-40 bg-white/80 backdrop-blur border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
          <div className="text-lg font-semibold">BCM AI Console</div>
          <div className="ml-auto flex items-center gap-2">
            <select value={client} onChange={(e)=>setClient(e.target.value)} className="rounded-xl border border-slate-300 px-3 py-1.5 text-sm">
              {mockClients.map((c)=> <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <div className="hidden md:flex items-center gap-2 bg-slate-100 rounded-xl px-3 py-1.5">
              <span>🔎</span>
              <input value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Search…" className="bg-transparent text-sm outline-none" />
            </div>
            <button onClick={()=>setAiOpen((v)=>!v)} className="px-3 py-1.5 rounded-xl bg-slate-900 text-white text-sm">{aiOpen?"Hide AI":"Show AI"}</button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-4 grid grid-cols-12 gap-4">
        {/* Sidebar */}
        <aside className="col-span-12 lg:col-span-2">
          <nav className="bg-white/80 backdrop-blur border border-slate-200 rounded-2xl p-2 sticky top-20">
            {modules.map((m)=> (
              <button key={m.key} onClick={()=>setActive(m.key)}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm mb-1 ${active===m.key?"bg-slate-900 text-white":"hover:bg-slate-100"}`}>
                <span className="shrink-0">{m.emoji}</span>
                <span>{m.label}</span>
              </button>
            ))}
          </nav>
        </aside>

        {/* Main */}
        <main className={`col-span-12 ${aiOpen?"lg:col-span-7":"lg:col-span-10"}`}>
          {content}
        </main>

        {/* AI Drawer */}
        {aiOpen && (
          <aside className="col-span-12 lg:col-span-3">
            <div className="bg-white/80 backdrop-blur border border-slate-200 rounded-2xl p-3 flex flex-col h-[calc(100vh-9.5rem)] sticky top-20">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">AI Assistant</h3>
                <Pill color="bg-indigo-600" text={clientName} />
              </div>
              <div className="flex-1 overflow-auto space-y-2">
                {aiMsgs.map((m,i)=> (
                  <div key={i} className={`text-sm p-2 rounded-xl ${m.role==="assistant"?"bg-indigo-50":"bg-slate-100"}`}>{m.text}</div>
                ))}
              </div>
              <div className="mt-3 flex items-center gap-2">
                <input value={aiInput} onChange={(e)=>setAiInput(e.target.value)}
                  onKeyDown={(e)=> e.key==='Enter' && sendAi()}
                  placeholder="Ask AI… e.g., Generate BCP draft"
                  className="flex-1 bg-white border border-slate-300 rounded-xl px-3 py-2 text-sm"/>
                <button onClick={sendAi} className="px-3 py-2 bg-indigo-600 text-white rounded-xl text-sm">Send</button>
              </div>
              <div className="mt-2 flex flex-wrap gap-2 text-xs">
                <button onClick={()=>setAiInput("Generate BCP draft for EHR")} className="px-2 py-1 rounded border">BCP draft</button>
                <button onClick={()=>setAiInput("Recommend tabletop scenario for Pharmacy") } className="px-2 py-1 rounded border">Scenario</button>
                <button onClick={()=>setAiInput("Summarize audit evidence for clause 8.4") } className="px-2 py-1 rounded border">Audit summary</button>
              </div>
            </div>
          </aside>
        )}
      </div>

      {/* Event log bottom */}
      <div className="max-w-7xl mx-auto px-4 pb-6">
        <div className="bg-white/80 backdrop-blur border border-slate-200 rounded-2xl p-3">
          <div className="text-xs text-slate-500 mb-2">Event Log</div>
          <div className="max-h-40 overflow-auto text-sm divide-y divide-slate-100">
            {events.map((e,i)=> (
              <div key={i} className="py-1.5 flex items-start gap-3"><span className="text-slate-400 w-28 shrink-0">{e.t}</span><span>{e.msg}</span></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
