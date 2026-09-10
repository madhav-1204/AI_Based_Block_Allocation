import { useState } from 'react'
import './App.css'

type Activity = { id: string; title: string; department: string; asset: string; due: string; duration: string; priority: 'Critical' | 'High' | 'Medium'; score: number }

const activities: Activity[] = [
  { id: 'TMS-4821', title: 'Ultrasonic rail flaw inspection', department: 'Engineering', asset: 'Track · KM 112/4', due: 'Due today', duration: '3h 30m', priority: 'Critical', score: 96 },
  { id: 'TDMS-1908', title: 'Replace isolator at feeder post', department: 'Traction', asset: 'OHE · FP-08', due: 'Due in 2 days', duration: '2h 00m', priority: 'High', score: 88 },
  { id: 'SMMS-7730', title: 'Reconfigure axle counter section', department: 'S&T', asset: 'Signal · AXC-44', due: 'Due in 3 days', duration: '1h 30m', priority: 'High', score: 82 },
  { id: 'TMS-4802', title: 'Tighten and pack joint sleepers', department: 'Engineering', asset: 'Track · KM 118/9', due: 'Due this week', duration: '2h 30m', priority: 'Medium', score: 68 },
]

const planBlocks = [
  { day: 'MON', date: '14 OCT', department: 'ENG', title: 'Rail flaw inspection', meta: 'NDLS–CNB · 112/4', time: '01:30 – 05:00', tone: 'coral' },
  { day: 'TUE', date: '15 OCT', department: 'OHE', title: 'Isolator replacement', meta: 'NDLS–CNB · FP-08', time: '02:00 – 04:00', tone: 'teal' },
  { day: 'WED', date: '16 OCT', department: 'S&T', title: 'Axle counter reconfigure', meta: 'CNB–ALD · AXC-44', time: '00:30 – 02:00', tone: 'gold' },
]

function App() {
  const [activeTab, setActiveTab] = useState('This week')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generated, setGenerated] = useState(false)
  const generatePlan = () => { setIsGenerating(true); window.setTimeout(() => { setIsGenerating(false); setGenerated(true) }, 650) }

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">/</span><span>RAIL<span className="brand-accent">SYNC</span></span></div>
      <div className="network-status"><span className="status-dot" /> Network live <span className="status-time">06:42 IST</span></div>
      <nav className="nav-list" aria-label="Primary navigation">
        <button className="nav-item active"><span className="nav-icon">▦</span> Command center</button><button className="nav-item"><span className="nav-icon">◫</span> Block planner <span className="nav-badge">4</span></button><button className="nav-item"><span className="nav-icon">⌁</span> Maintenance queue</button><button className="nav-item"><span className="nav-icon">◎</span> Corridor map</button><button className="nav-item"><span className="nav-icon">↗</span> Reports</button>
      </nav>
      <div className="sidebar-bottom"><div className="user-avatar">AS</div><div><strong>Arjun Sharma</strong><small>Divisional control</small></div><span className="more">•••</span></div>
    </aside>

    <section className="content">
      <header className="topbar"><div><div className="eyebrow">NORTH CENTRAL RAILWAY <span>/</span> PRAYAGRAJ DIVISION</div><h1>Command center</h1></div><div className="header-actions"><button className="icon-button" aria-label="Notifications">♧<span className="notification-dot" /></button><button className="outline-button">Export report <span>↗</span></button></div></header>
      <div className="accent-rule" />
      <div className="overview-row"><div><h2>Good morning, Arjun</h2><p className="muted">Here is what needs your attention across the network.</p></div><div className="last-sync"><span className="status-dot" /> Last sync 2 min ago <button className="refresh" aria-label="Refresh data">↻</button></div></div>

      <section className="metric-grid" aria-label="Network overview">
        <article className="metric-card dark"><div className="metric-label">ASSET AVAILABILITY <span className="info">i</span></div><div className="metric-value">94.8<span>%</span></div><div className="metric-footer up">↗ 2.4% <span>vs last week</span></div><div className="sparkline" /></article>
        <article className="metric-card"><div className="metric-label">ACTIVE BLOCKS <span className="info">i</span></div><div className="metric-value">12<span className="metric-unit"> / 18</span></div><div className="metric-footer"><span className="dark-text">6 slots available</span> <span>this week</span></div><div className="mini-bars"><i /><i /><i /><i /><i /><i /><i /></div></article>
        <article className="metric-card"><div className="metric-label">PENDING REQUESTS <span className="info">i</span></div><div className="metric-value">27</div><div className="metric-footer urgent">8 critical <span>need attention</span></div><div className="ring"><b>27</b><small>requests</small></div></article>
        <article className="metric-card"><div className="metric-label">TRAINS PROTECTED <span className="info">i</span></div><div className="metric-value">98.2<span>%</span></div><div className="metric-footer up">↗ 0.8% <span>on-time operations</span></div><div className="train-line">●━━━━●━━━━●━━━●</div></article>
      </section>

      <section className="main-grid">
        <article className="panel queue-panel"><div className="panel-heading"><div><div className="section-kicker">AI PRIORITIZATION ENGINE</div><h2>Maintenance queue</h2></div><button className="text-button">View all <span>→</span></button></div><p className="panel-intro">Ranked by asset criticality, overdue risk, and train impact.</p><div className="queue-list">{activities.map((activity) => <div className="queue-row" key={activity.id}><div className={`priority-bar ${activity.priority.toLowerCase()}`} /><div className="queue-main"><div className="queue-title"><strong>{activity.title}</strong><span className={`tag ${activity.priority.toLowerCase()}`}>{activity.priority}</span></div><div className="queue-meta"><span>{activity.department}</span><span>{activity.asset}</span><span>{activity.id}</span></div></div><div className="queue-due"><strong>{activity.due}</strong><span>{activity.duration}</span></div><div className="score"><b>{activity.score}</b><span>score</span></div></div>)}</div></article>
        <article className="panel corridor-panel"><div className="panel-heading"><div><div className="section-kicker">CORRIDOR HEALTH</div><h2>Network snapshot</h2></div><button className="map-button">Open map ↗</button></div><div className="corridor-map"><div className="map-grid" /><div className="route route-a"><span className="station start">NDLS</span><i /><i /><i /><span className="station">CNB</span><i /><i /><i /><span className="station end">ALD</span></div><div className="route-label label-a">NDLS — CNB <b>94%</b></div><div className="route route-b"><span className="station start">CNB</span><i /><i /><span className="station">ETW</span><i /><i /><span className="station end">ALD</span></div><div className="route-label label-b">CNB — ALD <b>89%</b></div><div className="map-legend"><span><i className="legend-live" /> Healthy</span><span><i className="legend-watch" /> Watch</span></div></div><div className="corridor-footer"><div><strong>6</strong><span>corridors monitored</span></div><div><strong>3</strong><span>under watch</span></div><div><strong>41</strong><span>assets at risk</span></div></div></article>
      </section>

      <section className="panel plan-panel"><div className="panel-heading plan-heading"><div><div className="section-kicker">COORDINATED BLOCK PLAN</div><h2>{generated ? 'Optimized plan ready' : 'Upcoming blocks'}</h2></div><div className="plan-controls"><div className="tabs">{['This week', 'Next week', 'Monthly view'].map((tab) => <button key={tab} className={activeTab === tab ? 'selected' : ''} onClick={() => setActiveTab(tab)}>{tab}</button>)}</div><button className="generate-button" onClick={generatePlan} disabled={isGenerating}>{isGenerating ? 'Optimizing...' : generated ? 'Plan generated ✓' : 'Generate plan'} <span>✦</span></button></div></div><div className="plan-summary"><span className="status-dot" /> {generated ? 'AI found 3 coordination opportunities' : '12 blocks scheduled'} <span className="separator">|</span> <span className="muted">{activeTab === 'Monthly view' ? 'October 2024' : '14 – 20 October 2024'}</span></div><div className="timeline">{planBlocks.map((block) => <div className="timeline-column" key={block.day}><div className="timeline-date"><b>{block.day}</b><span>{block.date}</span></div><div className="timeline-line" /><div className={`block-card ${block.tone}`}><div className="block-top"><span className="dept-code">{block.department}</span><span className="block-menu">•••</span></div><strong>{block.title}</strong><span>{block.meta}</span><time>{block.time}</time></div><div className="train-window"><span>Train window</span><b>08:00 – 12:00</b></div></div>)}</div></section>
      <footer className="footer"><span>RailSync planning engine v0.9</span><span>Data sources: TMS · SMMS · TDMS · COA</span><span>All times in IST</span></footer>
    </section>
  </main>
}

export default App
