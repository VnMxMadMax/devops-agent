import React, { useState, useEffect, useRef } from 'react';
import { ShieldAlert, Server, Activity, Terminal, CheckCircle, Zap } from 'lucide-react';
import './index.css';

const WS_URL = 'ws://localhost:8000/ws/simulation';
const API_URL = 'http://localhost:8000';

// Thresholds must match simulator/service.py per service
const SERVICE_THRESHOLDS = {
  'api-gateway': { cpu: 75, memory: 70, latency: 150, error_rate: 2.0 },
  'auth-service': { cpu: 65, memory: 65, latency: 120, error_rate: 1.5 },
  'order-service': { cpu: 85, memory: 80, latency: 200, error_rate: 3.0 },
  'payment-service': { cpu: 70, memory: 70, latency: 250, error_rate: 2.5 },
  'postgres-db': { cpu: 80, memory: 85, latency: 80, error_rate: 1.0 },
};

// Compute health from live metrics — svc.status from backend is static and unreliable
function getServiceHealth(svc) {
  const t = SERVICE_THRESHOLDS[svc.name];
  if (!t) return 'healthy';
  const m = svc.metrics;
  if (
    m.memory > t.memory ||
    m.cpu > t.cpu ||
    m.latency > t.latency ||
    m.error_rate > t.error_rate
  ) return 'critical';
  return 'healthy';
}

function App() {
  const [services, setServices] = useState([]);
  const [activeIncidents, setActiveIncidents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [wsStatus, setWsStatus] = useState('connecting');
  const [autoScroll, setAutoScroll] = useState(true);
  const [hasTriggeredBefore, setHasTriggeredBefore] = useState(false);
  const messagesEndRef = useRef(null);
  const streamRef = useRef(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/status`);
      const data = await res.json();
      setServices(data.services);
      setActiveIncidents(data.active_incidents);
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => setWsStatus('connected');
    ws.onclose = () => setWsStatus('disconnected');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Ignore heartbeats — they carry no agent information
      if (data.type === 'heartbeat') return;
      setMessages((prev) => [...prev, data]);
    };

    return () => ws.close();
  }, []);

  useEffect(() => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  // Pause auto-scroll the moment the user scrolls away from the bottom.
  // Resume the moment they scroll back to within 40px of the bottom.
  const handleStreamScroll = () => {
    const el = streamRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
    setAutoScroll(nearBottom);
  };

  const jumpToLatest = () => {
    setAutoScroll(true);
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const triggerRandomIncident = async () => {
    // First click of the session always triggers the auth-service memory leak —
    // it's the cleanest scenario to walk through on the demo video.
    // Subsequent clicks fall back to random selection.
    if (!hasTriggeredBefore) {
      await fetch(`${API_URL}/incident/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ incident_name: 'memory_leak_auth' })
      });
      setHasTriggeredBefore(true);
    } else {
      await fetch(`${API_URL}/incident/trigger/random`, {
        method: 'POST'
      });
    }
    fetchStatus();
  };

  const resolveActiveIncident = async () => {
    if (activeIncidents.length === 0) return;
    // Resolve the first active incident (could be any type)
    await fetch(`${API_URL}/incident/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ incident_name: activeIncidents[0] })
    });
    fetchStatus();
  };

  const hasActiveIncident = activeIncidents.length > 0;

  return (
    <div className="app-container">
      <header className="header">
        <div className="title-container">
          <div className="logo">
            <Zap size={24} color="#fff" />
          </div>
          <h1 className="title">Sentinel AI Dashboard</h1>
        </div>

        <div className="controls">
          <button
            id="btn-trigger-incident"
            className="btn btn-trigger"
            onClick={triggerRandomIncident}
            disabled={hasActiveIncident}
          >
            <ShieldAlert size={16} />
            Trigger Incident
          </button>

          <button
            id="btn-resolve-incident"
            className="btn btn-resolve"
            onClick={resolveActiveIncident}
            disabled={!hasActiveIncident}
          >
            <CheckCircle size={16} />
            Resolve Incident
          </button>

          <div className="status-badge">
            <div className={`status-dot ${hasActiveIncident || wsStatus !== 'connected' ? 'active-incident' : ''}`} />
            {wsStatus !== 'connected'
              ? 'Disconnected'
              : hasActiveIncident ? 'Incident Active' : 'Live'}
          </div>
        </div>
      </header>

      <main className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <Server size={20} />
              Service Health
            </h2>
          </div>
          <div className="panel-content services-list">
            {services.map((svc) => {
              const health = getServiceHealth(svc);
              return (
                <div
                  key={svc.name}
                  className={`service-card ${health === 'critical' ? 'critical' : ''}`}
                >
                  <div className="service-header">
                    <span className="service-name">{svc.name}</span>
                    <span className={`service-health ${health === 'healthy' ? 'health-healthy' : 'health-unhealthy'}`}>
                      {health}
                    </span>
                  </div>
                  <div className="metrics-grid">
                    <div className="metric-item">
                      <span className="metric-label">CPU</span>
                      <span className="metric-value">{svc.metrics.cpu.toFixed(1)}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Memory</span>
                      <span className="metric-value">{svc.metrics.memory.toFixed(1)}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Latency</span>
                      <span className="metric-value">{svc.metrics.latency.toFixed(0)}ms</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Error Rate</span>
                      <span className="metric-value">{svc.metrics.error_rate.toFixed(2)}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <Terminal size={20} />
              Agent Event Stream
            </h2>
          </div>
          <div
            className="panel-content stream-container"
            ref={streamRef}
            onScroll={handleStreamScroll}
          >
            {messages.length === 0 ? (
              <div style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '2rem' }}>
                Waiting for agent activity...
              </div>
            ) : (
              messages.map((msg, i) => (
                <div key={i} className="message-item">
                  <div className="message-header">
                    <Activity size={14} />
                    <span className={`message-type type-${msg.type}`}>
                      {msg.type.replace('Message', '')}
                    </span>
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
            {!autoScroll && messages.length > 0 && (
              <button
                className="jump-to-latest"
                onClick={jumpToLatest}
                aria-label="Jump to latest message"
              >
                ↓ Jump to latest
              </button>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
