import { useState, useEffect } from "react"
import { useAuth } from "../App"

const GOLD = "#D4AF37"
const af = (url, token, opts = {}) => fetch(url, { ...opts, headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(opts.headers||{}) }})

const PLATFORMS = {
  youtube:    { label: "YouTube",    url: "https://www.youtube.com/@ForgedInIceShorts", icon: "▶" },
  tiktok:     { label: "TikTok",     url: "https://www.tiktok.com/@forgedinice.tribe",  icon: "◈" },
  instagram:  { label: "Instagram",  url: "https://www.instagram.com/forged_in_ice_tribe/", icon: "◎" },
  facebook:   { label: "Facebook",   url: "https://www.facebook.com/forgedinice.tribe/", icon: "◉" },
  soundcloud: { label: "SoundCloud", url: "https://soundcloud.com/forgedinice",          icon: "♪" },
}

export default function Rewards() {
  const { token, API } = useAuth()
  const [discount, setDiscount] = useState(null)
  const [status, setStatus]     = useState(null)
  const [loading, setLoading]   = useState(true)
  const [followLoading, setFollowLoading] = useState({})
  const [followMsg, setFollowMsg]         = useState({})
  const [email, setEmail] = useState("")
  const [nlMsg, setNlMsg] = useState("")
  const [copied, setCopied] = useState(false)

  const load = () => Promise.all([
    af(`${API}/rewards/discount`, token).then(r => r.json()),
    af(`${API}/rewards/status`, token).then(r => r.json()),
  ]).then(([d, s]) => { setDiscount(d); setStatus(s) }).finally(() => setLoading(false))

  useEffect(() => { load() }, [token])

  const recordFollow = async (platform) => {
    setFollowLoading(p => ({ ...p, [platform]: true }))
    setFollowMsg(p => ({ ...p, [platform]: "" }))
    try {
      const res = await af(`${API}/rewards/social-follow`, token, { method: "POST", body: JSON.stringify({ platform }) })
      const data = await res.json()
      if (data.status === "already_recorded") setFollowMsg(p => ({ ...p, [platform]: "Already recorded" }))
      else { setFollowMsg(p => ({ ...p, [platform]: `+${data.xp_awarded} XP${data.all_platforms_bonus ? " +50 bonus!" : ""}` })); load() }
    } catch { setFollowMsg(p => ({ ...p, [platform]: "Error — try again" })) }
    finally { setFollowLoading(p => ({ ...p, [platform]: false })) }
  }

  const signupNewsletter = async (e) => {
    e.preventDefault()
    try {
      const res = await af(`${API}/rewards/newsletter-signup`, token, { method: "POST", body: JSON.stringify({ email }) })
      const data = await res.json()
      setNlMsg(data.status === "already_recorded" ? "Already subscribed ✓" : `+${data.xp_awarded} XP awarded ✓`)
    } catch { setNlMsg("Error — try again") }
  }

  const copyCode = () => {
    if (discount?.promo_code) { navigator.clipboard.writeText(discount.promo_code); setCopied(true); setTimeout(() => setCopied(false), 2000) }
  }

  if (loading) return <div style={{ color: "#555", padding: "4rem", textAlign: "center" }}>Loading rewards...</div>

  return (
    <div>
      <h2 style={{ color: GOLD, marginTop: 0, marginBottom: 4 }}>Rewards</h2>
      <p style={{ color: "#555", fontSize: 13, marginTop: 0, marginBottom: "1.5rem" }}>Earn XP by following, subscribing and purchasing. Higher rank = bigger discounts and more freebies.</p>

      <div style={{ background: "#0d0d0d", border: `1px solid ${GOLD}33`, borderRadius: 8, padding: "1.25rem", marginBottom: "1.5rem" }}>
        <div style={{ color: "#888", fontSize: 11, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>Your Payhip discount</div>
        {discount?.discount_pct > 0 ? (
          <>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
              <div style={{ color: GOLD, fontSize: 32, fontWeight: 700 }}>{discount.discount_pct}% off</div>
              <div style={{ color: "#555", fontSize: 13 }}>on all purchases at <a href={discount.payhip_store} target="_blank" rel="noreferrer" style={{ color: GOLD }}>payhip.com/ForgedInIceVaults</a></div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <code style={{ background: "#111", border: "1px solid #333", borderRadius: 4, padding: "8px 14px", fontSize: 14, color: "#fff", letterSpacing: 2 }}>{discount.promo_code}</code>
              <button onClick={copyCode} style={{ background: copied ? GOLD : "transparent", color: copied ? "#000" : GOLD, border: `1px solid ${GOLD}`, borderRadius: 4, padding: "8px 14px", cursor: "pointer", fontSize: 12 }}>
                {copied ? "Copied ✓" : "Copy code"}
              </button>
            </div>
            <div style={{ color: "#444", fontSize: 12, marginTop: 8 }}>{discount.instructions}</div>
          </>
        ) : (
          <div style={{ color: "#555", fontSize: 13 }}>Reach <span style={{ color: GOLD }}>The Watcher</span> rank (100 XP) to unlock your first discount. Follow all 5 platforms to earn 175 XP instantly.</div>
        )}
      </div>

      <div style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "1.25rem", marginBottom: "1.5rem" }}>
        <div style={{ color: "#888", fontSize: 11, textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>Follow for XP</div>
        <div style={{ color: "#444", fontSize: 12, marginBottom: 12 }}>+25 XP per platform. +50 bonus when all 5 are followed.</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {Object.entries(PLATFORMS).map(([key, p]) => {
            const followed = status?.platforms_followed?.includes(key)
            return (
              <div key={key} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <a href={p.url} target="_blank" rel="noreferrer" style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "#111", border: "1px solid #333", borderRadius: 4, padding: "8px 14px", color: "#ccc", fontSize: 13, textDecoration: "none", minWidth: 140 }}>
                  <span>{p.icon}</span> {p.label}
                </a>
                <button onClick={() => recordFollow(key)} disabled={followed || followLoading[key]} style={{ background: followed ? "#1a1a0a" : "transparent", color: followed ? GOLD : "#555", border: `1px solid ${followed ? GOLD : "#333"}`, borderRadius: 4, padding: "8px 14px", cursor: followed ? "default" : "pointer", fontSize: 12 }}>
                  {followLoading[key] ? "..." : followed ? "✓ Recorded" : "Record follow +25 XP"}
                </button>
                {followMsg[key] && <span style={{ color: GOLD, fontSize: 12 }}>{followMsg[key]}</span>}
              </div>
            )
          })}
        </div>
      </div>

      <div style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "1.25rem", marginBottom: "1.5rem" }}>
        <div style={{ color: "#888", fontSize: 11, textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>Newsletter — +15 XP</div>
        <div style={{ color: "#444", fontSize: 12, marginBottom: 12 }}>Each issue links all socials, drops freebies by rank, and surfaces new content before anywhere else.</div>
        <form onSubmit={signupNewsletter} style={{ display: "flex", gap: 8 }}>
          <input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="your@email.com" required
            style={{ flex: 1, background: "#111", border: "1px solid #333", borderRadius: 4, padding: "8px 12px", color: "#fff", fontSize: 13 }} />
          <button type="submit" style={{ background: GOLD, color: "#000", border: "none", borderRadius: 4, padding: "8px 16px", cursor: "pointer", fontSize: 13, fontWeight: 700 }}>Subscribe +15 XP</button>
        </form>
        {nlMsg && <div style={{ color: GOLD, fontSize: 12, marginTop: 8 }}>{nlMsg}</div>}
      </div>

      <div style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "1.25rem" }}>
        <div style={{ color: "#888", fontSize: 11, textTransform: "uppercase", letterSpacing: 1, marginBottom: 12 }}>All discount tiers</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {discount?.all_tiers?.map((t, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px", borderRadius: 6, background: t.rank === status?.observer_rank ? "#111" : "transparent", border: t.rank === status?.observer_rank ? `1px solid ${GOLD}44` : "1px solid transparent" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ color: t.unlocked ? GOLD : "#333", fontSize: 12 }}>{t.unlocked ? "✓" : "○"}</span>
                <span style={{ color: t.unlocked ? "#ccc" : "#333", fontSize: 13 }}>{t.rank}</span>
                {t.rank === status?.observer_rank && <span style={{ background: GOLD, color: "#000", fontSize: 10, padding: "1px 6px", borderRadius: 10, fontWeight: 700 }}>YOU</span>}
              </div>
              <span style={{ color: t.discount_pct > 0 ? GOLD : "#333", fontSize: 13, fontWeight: t.unlocked ? 700 : 400 }}>{t.discount_pct > 0 ? `${t.discount_pct}% off` : "—"}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
