import { useState, useEffect } from "react"
import { useAuth } from "../App"

const GOLD = "#D4AF37"
const af = (url, token, opts = {}) => fetch(url, { ...opts, headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(opts.headers||{}) }})
const TYPE_ICON  = { clip: "▶", music: "♪", art: "◈", lore: "◉" }
const TYPE_LABEL = { clip: "Watcher clip", music: "Suno track", art: "Canon artwork", lore: "Lore fragment" }

export default function Freebies() {
  const { token, API } = useAuth()
  const [data, setData]         = useState(null)
  const [loading, setLoading]   = useState(true)
  const [claiming, setClaiming] = useState({})
  const [claimed, setClaimed]   = useState({})
  const [errors, setErrors]     = useState({})

  useEffect(() => {
    af(`${API}/rewards/freebies`, token).then(r => r.json()).then(setData).finally(() => setLoading(false))
  }, [token])

  const claim = async (key) => {
    setClaiming(p => ({ ...p, [key]: true })); setErrors(p => ({ ...p, [key]: "" }))
    try {
      const res = await af(`${API}/rewards/freebies/claim`, token, { method: "POST", body: JSON.stringify({ freebie_key: key }) })
      const result = await res.json()
      if (!res.ok) throw new Error(result.detail || "Error")
      setClaimed(p => ({ ...p, [key]: true }))
    } catch (err) { setErrors(p => ({ ...p, [key]: err.message })) }
    finally { setClaiming(p => ({ ...p, [key]: false })) }
  }

  if (loading) return <div style={{ color: "#555", padding: "4rem", textAlign: "center" }}>Loading freebies...</div>

  const grouped = (data?.freebies || []).reduce((acc, f) => { if (!acc[f.type]) acc[f.type] = []; acc[f.type].push(f); return acc }, {})

  return (
    <div>
      <h2 style={{ color: GOLD, marginTop: 0, marginBottom: 4 }}>Freebies</h2>
      <p style={{ color: "#555", fontSize: 13, marginTop: 0, marginBottom: "1.5rem" }}>
        Rank-gated content. Your rank: <span style={{ color: GOLD }}>{data?.current_rank}</span> — {data?.unlocked_count} items unlocked.
      </p>

      {data?.unlocked_count === 0 && (
        <div style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "2rem", textAlign: "center" }}>
          <div style={{ color: "#444", fontSize: 14, marginBottom: 8 }}>No freebies unlocked yet.</div>
          <div style={{ color: "#333", fontSize: 13 }}>Reach <span style={{ color: GOLD }}>The Watcher</span> rank (100 XP) to unlock your first clips and tracks.<br/>Follow all 5 socials to earn 175 XP in one session.</div>
        </div>
      )}

      {["clip","music","art","lore"].map(type => {
        const items = grouped[type]
        if (!items?.length) return null
        return (
          <div key={type} style={{ marginBottom: "1.5rem" }}>
            <div style={{ color: "#888", fontSize: 11, textTransform: "uppercase", letterSpacing: 1, marginBottom: 10 }}>{TYPE_ICON[type]} {TYPE_LABEL[type]}s</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {items.map(item => (
                <div key={item.key} style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 6, padding: "12px 16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div>
                    <div style={{ color: "#ccc", fontSize: 14 }}>{item.title}</div>
                    <div style={{ color: "#444", fontSize: 11, marginTop: 2 }}>{TYPE_LABEL[type]}</div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    {errors[item.key] && <span style={{ color: "#e05", fontSize: 12 }}>{errors[item.key]}</span>}
                    {claimed[item.key]
                      ? <a href={item.url} download style={{ background: GOLD, color: "#000", borderRadius: 4, padding: "6px 14px", fontSize: 12, fontWeight: 700, textDecoration: "none" }}>Download ↓</a>
                      : <button onClick={() => claim(item.key)} disabled={claiming[item.key]} style={{ background: "transparent", color: GOLD, border: `1px solid ${GOLD}`, borderRadius: 4, padding: "6px 14px", cursor: "pointer", fontSize: 12 }}>{claiming[item.key] ? "..." : "Claim +5 XP"}</button>
                    }
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      })}

      {data?.current_rank !== "The Unseen" && (
        <div style={{ background: "#080808", border: "1px dashed #222", borderRadius: 8, padding: "1.25rem" }}>
          <div style={{ color: "#333", fontSize: 12, marginBottom: 6 }}>More freebies locked at higher ranks</div>
          <div style={{ color: "#222", fontSize: 12 }}>Clips 04–06 · Tracks 03–04 · Canon artworks · Lore fragments 001–003</div>
          <div style={{ color: "#333", fontSize: 12, marginTop: 8 }}>Earn more XP via purchases (+50 base + 1 XP/£), follows (+25 each) and shares (+20 each).</div>
        </div>
      )}
    </div>
  )
}
