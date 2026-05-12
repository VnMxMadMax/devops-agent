import React, { useState, useEffect, useRef } from 'react';
import { ShieldAlert, Server, Activity, Terminal, CheckCircle, Zap } from 'lucide-react';
import './index.css';

const WS_URL = 'ws://localhost:8000/ws/simulation';
const API_URL = 'http://localhost:8000';

function App() {
  const [services, setServices] = useState([]);
  const [activeIncidents, setActiveIncidents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [wsStatus, setWsStatus] = useState('connecting');
  const messagesEndRef = useRef(null);

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
      if (data.type === 'heartbeat') return; // Ignore heartbeats in UI
      
      setMessages((prev) => [...prev, data]);
    };

    return () => ws.close();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const triggerIncident = async (name) => {
    await fetch(`${API_URL}/incident/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ incident_name: name })
    });
    fetchStatus();
  };

  const resolveIncident = async (name) => {
    await fetch(`${API_URL}/incident/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ incident_name: name })
    });
    fetchStatus();
  };

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
            className="btn btn-trigger"
            onClick={() => triggerIncident('memory_leak_auth')}
            disabled={activeIncidents.includes('memory_leak_auth')}
          >
            <ShieldAlert size={16} />
            Trigger Memory Leak
          </button>
          
          <button 
            className="btn btn-resolve"
            onClick={() => resolveIncident('memory_leak_auth')}
            disabled={!activeIncidents.includes('memory_leak_auth')}
          >
            <CheckCircle size={16} />
            Resolve Incident
          </button>
          
          <div className="status-badge">
            <div className={`status-dot ${wsStatus === 'connected' ? '' : 'active-incident'}`} />
            {wsStatus === 'connected' ? 'Live' : 'Disconnected'}
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
            {services.map((svc) => (
              <div 
                key={svc.name} 
                className={`service-card ${svc.status !== 'healthy' ? 'critical' : ''}`}
              >
                <div className="service-header">
                  <span className="service-name">{svc.name}</span>
                  <span className={`service-health ${svc.status === 'healthy' ? 'health-healthy' : 'health-unhealthy'}`}>
                    {svc.status}
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
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <Terminal size={20} />
              Agent Event Stream
            </h2>
          </div>
          <div className="panel-content stream-container">
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
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
