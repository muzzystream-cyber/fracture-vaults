import { useState } from "react"
import { useAuth } from "../App"

const GOLD = "#D4AF37"
const inp = { background: "#111", border: "1px solid #333", borderRadius: 4, padding: "10px 12px", color: "#fff", fontSize: 14, width: "100%" }

export default function Login({ onSwitch }) {
  const { setToken, API } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true); setError("")
    try {
      const form = new URLSearchParams()
      form.append("username", email)
      form.append("password", password)
      const res = await fetch(`${API}/auth/login`, { method: "POST", body: form })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Login failed")
      setToken(data.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ width: 360, background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "2rem" }}>
      <div style={{ color: GOLD, fontSize: 24, fontWeight: 700, textAlign: "center", marginBottom: 4 }}>👁️ FRACTURE VAULTS</div>
      <div style={{ color: "#555", fontSize: 12, textAlign: "center", marginBottom: 24, letterSpacing: 1 }}>THE PATTERN IS VISIBLE</div>
      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="Email" required style={inp} />
        <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Password" required style={inp} />
        {error && <div style={{ color: "#e05", fontSize: 13 }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ background: GOLD, color: "#000", border: "none", borderRadius: 4, padding: "12px", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
          {loading ? "Entering..." : "Enter the Vaults"}
        </button>
      </form>
      <div style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "#555" }}>
        No account?{" "}
        <button onClick={onSwitch} style={{ background: "none", border: "none", color: GOLD, cursor: "pointer", fontSize: 13 }}>Register</button>
      </div>
    </div>
  )
}
