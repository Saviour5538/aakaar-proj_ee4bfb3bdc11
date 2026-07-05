import { useState } from "react";

// Ask-a-question (RAG) screen. Talks to the deterministic backend endpoint
// POST /api/ai/query  { query, session_id } -> { answer, sources: string[] }.
const API = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

export default function Chat() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const ask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true); setError(""); setAnswer(""); setSources([]);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/api/ai/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ query, session_id: "default" }),
      });
      if (!res.ok) throw new Error(`Query failed (${res.status})`);
      const data = await res.json();
      setAnswer(data.answer || "");
      setSources(data.sources || []);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 760, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Ask your documents</h1>
      <form onSubmit={ask} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your uploaded documents…"
          style={{ flex: 1, padding: 10 }}
        />
        <button type="submit" disabled={loading} style={{ padding: "10px 18px" }}>
          {loading ? "Thinking…" : "Ask"}
        </button>
      </form>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {answer && (
        <div>
          <h3>Answer</h3>
          <p style={{ whiteSpace: "pre-wrap" }}>{answer}</p>
          {sources.length > 0 && (
            <div>
              <h4>Sources</h4>
              <ul>{sources.map((s, i) => <li key={i}>{s}</li>)}</ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
