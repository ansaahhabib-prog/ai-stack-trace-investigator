import React, { useState } from 'react';
import axios from 'axios';
import { Search, Play, AlertCircle, CheckCircle, Terminal, HelpCircle, Activity } from 'lucide-react';
import type { AnalysisResult, SandboxResult } from './types';
import './index.css';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [errorInput, setErrorInput] = useState('');
  const [codeContext, setCodeContext] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [apiError, setApiError] = useState('');

  const [isRunningSandbox, setIsRunningSandbox] = useState(false);
  const [sandboxResult, setSandboxResult] = useState<SandboxResult | null>(null);

  const handleAnalyze = async () => {
    if (!errorInput.trim()) {
      setApiError('Please provide a stack trace to analyze.');
      return;
    }
    
    setIsAnalyzing(true);
    setApiError('');
    setAnalysisResult(null);
    setSandboxResult(null);

    try {
      const response = await axios.post<AnalysisResult>(`${API_URL}/analyze`, {
        error_input: errorInput,
        code_context: codeContext || undefined,
      });
      setAnalysisResult(response.data);
    } catch (err: any) {
      console.error(err);
      setApiError(err.response?.data?.detail || err.message || 'Failed to analyze stack trace');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRunSandbox = async () => {
    if (!analysisResult?.reproduction_code) return;
    
    setIsRunningSandbox(true);
    setSandboxResult(null);

    try {
      const response = await axios.post<SandboxResult>(`${API_URL}/run-sandbox`, {
        reproduction_code: analysisResult.reproduction_code,
      });
      setSandboxResult(response.data);
    } catch (err: any) {
      console.error(err);
      setSandboxResult({
        status: 'error',
        message: err.response?.data?.detail || err.message || 'Failed to run in sandbox',
      });
    } finally {
      setIsRunningSandbox(false);
    }
  };

  return (
    <div>
      <header className="header">
        <h1>AI Stack Trace Investigator</h1>
        <p>Analyze stack traces using AI and run reproduction code in a secure sandbox.</p>
      </header>

      <main className="container">
        {/* Left Column - Inputs */}
        <div className="glass-panel">
          <h2><Activity size={24} /> Input Data</h2>
          
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>
              Stack Trace / Error Output *
            </label>
            <textarea
              placeholder="Paste your stack trace or error log here..."
              value={errorInput}
              onChange={(e) => setErrorInput(e.target.value)}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>
              Relevant Source Code (Optional)
            </label>
            <textarea
              placeholder="Paste any relevant source code that might provide context..."
              value={codeContext}
              onChange={(e) => setCodeContext(e.target.value)}
              style={{ minHeight: '150px' }}
            />
          </div>

          {apiError && (
            <div className="error-msg">
              <AlertCircle size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'text-bottom' }}/>
              {apiError}
            </div>
          )}

          <button 
            className="btn" 
            onClick={handleAnalyze}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <><span className="loader"></span> Analyzing...</>
            ) : (
              <><Search size={20} /> Analyze Stack Trace</>
            )}
          </button>
        </div>

        {/* Right Column - Results */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <h2><Terminal size={24} /> Analysis Results</h2>
          
          {!analysisResult && !isAnalyzing && (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              Submit a stack trace to see the analysis results here.
            </div>
          )}

          {isAnalyzing && (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
              <span className="loader" style={{ width: '3rem', height: '3rem', borderTopColor: 'var(--primary)', marginBottom: '1rem' }}></span>
              <p>AI is investigating the stack trace...</p>
            </div>
          )}

          {analysisResult && (
            <div className="results-section">
              {/* Causes */}
              {analysisResult.causes && analysisResult.causes.length > 0 && (
                <div style={{ marginBottom: '2rem' }}>
                  <h3 style={{ marginBottom: '1rem', color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertCircle size={20} color="var(--warning)" /> Likely Causes
                  </h3>
                  {analysisResult.causes.map((cause, idx) => (
                    <div key={idx} className="cause-card">
                      <div className="cause-header">
                        <span className="cause-title">Cause {idx + 1}: {cause.description}</span>
                        <span className="likelihood">{cause.likelihood}</span>
                      </div>
                      <div className="fix-suggestion">
                        <strong>Fix Suggestion:</strong><br />
                        {cause.fix_suggestion}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Missing Evidence */}
              {analysisResult.missing_evidence && analysisResult.missing_evidence.length > 0 && (
                <div style={{ marginBottom: '2rem' }}>
                  <h3 style={{ marginBottom: '1rem', color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <HelpCircle size={20} color="var(--primary)" /> Questions / Missing Info
                  </h3>
                  <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-muted)' }}>
                    {analysisResult.missing_evidence.map((item, idx) => (
                      <li key={idx} style={{ marginBottom: '0.5rem' }}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Reproduction Code */}
              {analysisResult.reproduction_code && (
                <div>
                  <h3 style={{ marginBottom: '1rem', color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Terminal size={20} color="var(--success)" /> Reproduction Code
                  </h3>
                  <div className="code-block">
                    <pre>{analysisResult.reproduction_code}</pre>
                  </div>
                  
                  <button 
                    className="btn btn-secondary" 
                    onClick={handleRunSandbox}
                    disabled={isRunningSandbox}
                  >
                    {isRunningSandbox ? (
                      <><span className="loader"></span> Running...</>
                    ) : (
                      <><Play size={20} /> Run in Sandbox 🚀</>
                    )}
                  </button>

                  {/* Sandbox Result */}
                  {sandboxResult && (
                    <div style={{ marginTop: '1.5rem', animation: 'fadeIn 0.3s ease-out' }}>
                      {sandboxResult.status === 'success' ? (
                        <>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: sandboxResult.exit_code === 0 ? 'var(--success)' : 'var(--danger)' }}>
                            {sandboxResult.exit_code === 0 ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                            <strong style={{ fontSize: '1.1rem' }}>
                              Sandbox Executed (Exit Code: {sandboxResult.exit_code})
                            </strong>
                          </div>
                          {sandboxResult.logs && (
                            <div className="sandbox-logs">
                              {sandboxResult.logs}
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="error-msg">
                          <AlertCircle size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'text-bottom' }}/>
                          <strong>Sandbox Error:</strong> {sandboxResult.message}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
