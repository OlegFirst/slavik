import React from 'react';
import '@/globals.css';

function App() {
  return (
    <div style={{ padding: '50px', textAlign: 'center', fontFamily: 'system-ui' }}>
      <h1 style={{ fontSize: '3rem', color: '#2563eb', marginBottom: '20px' }}>
        🚀 BCM Admin Panel
      </h1>
      <p style={{ fontSize: '1.5rem', color: '#64748b' }}>
        Dashboard is loading...
      </p>
      <div style={{ marginTop: '30px', padding: '20px', border: '2px solid #e2e8f0', borderRadius: '12px', backgroundColor: '#f1f5f9' }}>
        <p style={{ color: '#1e293b' }}>
          The application is working!
        </p>
        <p style={{ color: '#475569', marginTop: '10px' }}>
          Check console for any errors.
        </p>
      </div>
    </div>
  );
}

export default App;