import { useState } from "react"
import { useAuth } from "../App"

const GOLD = "#D4AF37"
const inp = { background: "#111", border: "1px solid #333", borderRadius: 4, padding: "10px 12px", color: "#fff", fontSize: 14, width: "100%" }

export default function Register({ onSwitch }) {
  const { setToken, API } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true); setError("")
    try {
      const res = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Registration failed")
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
      <div style={{ color: "#555", fontSize: 12, textAlign: "center", marginBottom: 24, letterSpacing: 1 }}>BEGIN THE RECORD</div>
      <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="Email" required style={inp} />
        <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Password (min 8 chars)" required minLength={8} style={inp} />
        {error && <div style={{ color: "#e05", fontSize: 13 }}>{error}</div>}
        <div style={{ color: "#444", fontSize: 11, lineHeight: 1.6 }}>
          +10 XP on registration. Follow all 5 platforms for +175 XP. Purchases award +50 XP base + 1 XP/£.
        </div>
        <button type="submit" disabled={loading} style={{ background: GOLD, color: "#000", border: "none", borderRadius: 4, padding: "12px", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
          {loading ? "Registering..." : "Enter the Vaults"}
        </button>
      </form>
      <div style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: "#555" }}>
        Already registered?{" "}
        <button onClick={onSwitch} style={{ background: "none", border: "none", color: GOLD, cursor: "pointer", fontSize: 13 }}>Sign in</button>
      </div>
    </div>
  )
}
