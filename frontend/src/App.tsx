import { useState } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './App.css'

const API = (import.meta.env.VITE_API_URL || 'https://codecomplexity-api.vercel.app').replace(/\/$/, '')
const defaultCode = `def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(10))`

type Analysis = {
  time: string
  auxiliary_space: string
  input_space: string
  recursion_stack: string
  confidence: string
  counts: Record<string, number>
  findings: Array<{ line: number; kind: string; explanation: string; complexity: string }>
}

function App() {
  const [source, setSource] = useState(defaultCode)
  const [input, setInput] = useState('')
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [runtime, setRuntime] = useState<{ status: string; stdout: string; stderr: string; executionTimeMs: number; security: string } | null>(null)
  const [benchmarks, setBenchmarks] = useState<Array<{ inputSize: number; averageMs: number }>>([])
  const [active, setActive] = useState('Playground')
  const [busy, setBusy] = useState(false)
  const [theme, setTheme] = useState<'vs-dark' | 'light'>('vs-dark')

  async function run() {
    setBusy(true)
    try {
      const [execution, staticResult] = await Promise.all([
        axios.post(`${API}/api/execute`, { language: 'python', source, input }),
        axios.post(`${API}/api/analyze/static`, { language: 'python', source }),
      ])
      setRuntime(execution.data)
      setAnalysis(staticResult.data)
    } catch (error) {
      setRuntime({ status: 'error', stdout: '', stderr: axios.isAxiosError(error) ? error.message : 'Backend request failed', executionTimeMs: 0, security: 'Development mode' })
    } finally { setBusy(false) }
  }

  async function benchmark() {
    setBusy(true)
    try {
      const result = await axios.post(`${API}/api/benchmark`, { language: 'python', source, sizes: [100, 500, 1000, 5000, 10000], repeats: 3 })
      setBenchmarks(result.data.empirical.filter((item: { averageMs: number | null }) => item.averageMs !== null))
      setAnalysis(result.data.static)
    } finally { setBusy(false) }
  }

  const nav = ['Dashboard', 'Playground', 'Benchmark', 'Compare', 'Learn', 'Quiz', 'History']

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">V</span><span>Venu Compiler</span></div>
        <nav>{nav.map((item) => <button key={item} className={active === item ? 'nav-item active' : 'nav-item'} onClick={() => setActive(item)}>{item}</button>)}</nav>
        <button className="theme-toggle" onClick={() => setTheme(theme === 'vs-dark' ? 'light' : 'vs-dark')}>{theme === 'vs-dark' ? 'Light mode' : 'Dark mode'}</button>
      </aside>
      <main>
        <header className="topbar">
          <div><p className="eyebrow">VENU COMPILER</p><h1>{active}</h1></div>
          <div className="top-actions">
            <select aria-label="Programming language"><option>Python 3</option></select>
            <button className="secondary" onClick={() => setSource(defaultCode)}>Reset</button>
            <button className="primary" onClick={run} disabled={busy}>{busy ? 'Working...' : 'Run & Analyze'}</button>
          </div>
        </header>
        {active === 'Learn' ? (
          <section className="learning-grid">
            {[
              ['Big-O Notation', 'Describes an upper bound on growth as input size increases.'],
              ['Loops', 'Sequential loops add; nested loops multiply.'],
              ['Recursion', 'Measure recursive branch count and maximum call-stack depth.'],
              ['Sorting', 'Python sort is typically O(n log n); auxiliary memory is implementation-specific.'],
            ].map(([title, text]) => <article className="card" key={title}><h2>{title}</h2><p>{text}</p></article>)}
          </section>
        ) : active === 'Quiz' ? (
          <section className="card quiz-card"><p className="eyebrow">COMPLEXITY CHALLENGE</p><h2>What is the time complexity of binary search?</h2><div className="quiz-options">{['O(1)', 'O(log n)', 'O(n)', 'O(n²)'].map((option) => <button key={option}>{option}</button>)}</div></section>
        ) : (
          <>
            <section className="workspace">
              <div className="editor-card">
                <div className="panel-heading"><strong>main.py</strong><span>Python 3</span></div>
                <Editor height="420px" language="python" value={source} theme={theme} onChange={(value) => setSource(value || '')} options={{ minimap: { enabled: false }, fontSize: 14 }} />
              </div>
              <aside className="analysis-card">
                <div className="panel-heading"><strong>Complexity Analysis</strong><span>{analysis?.confidence || 'Ready'}</span></div>
                {analysis ? (
                  <div className="analysis-body">
                    <div className="complexity-primary"><span>Estimated time</span><strong>{analysis.time}</strong></div>
                    <div className="metric-grid"><div><span>Auxiliary</span><strong>{analysis.auxiliary_space}</strong></div><div><span>Input</span><strong>{analysis.input_space}</strong></div><div><span>Recursion</span><strong>{analysis.recursion_stack}</strong></div></div>
                    <h3>Detected patterns</h3>
                    <div className="chips">{Object.entries(analysis.counts).map(([key, value]) => <span key={key}>{key.replaceAll('_', ' ')}: {value}</span>)}</div>
                    <h3>Line analysis</h3>
                    <div className="finding-list">{analysis.findings.slice(0, 6).map((finding, index) => <button key={index}><b>Line {finding.line}</b><span>{finding.explanation}</span><em>{finding.complexity}</em></button>)}</div>
                  </div>
                ) : <div className="empty-state">Run your code to generate a complexity report.</div>}
              </aside>
            </section>
            <section className="bottom-grid">
              <div className="console-card">
                <div className="tabs"><strong>Input</strong><strong>Output</strong><strong>Console</strong></div>
                <textarea value={input} onChange={(event) => setInput(event.target.value)} placeholder="Enter custom input..." />
                <pre>{runtime ? `${runtime.stdout}${runtime.stderr}` : 'Output will appear here.'}</pre>
                {runtime && <div className="runtime-meta"><span>{runtime.status}</span><span>{runtime.executionTimeMs} ms</span><span>{runtime.security}</span></div>}
              </div>
              <div className="chart-card">
                <div className="panel-heading"><strong>Benchmark trend</strong><button onClick={benchmark} disabled={busy}>Benchmark</button></div>
                {benchmarks.length ? <ResponsiveContainer width="100%" height={210}><LineChart data={benchmarks}><CartesianGrid strokeDasharray="3 3" stroke="#26324a" /><XAxis dataKey="inputSize" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Line type="monotone" dataKey="averageMs" stroke="#8b5cf6" strokeWidth={3} dot /></LineChart></ResponsiveContainer> : <div className="empty-chart">Run a benchmark to plot scaling behavior.</div>}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  )
}

export default App
