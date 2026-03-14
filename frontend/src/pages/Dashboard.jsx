import { useState, useEffect } from "react"
import { useAuth } from "../App"
import RankCard from "../components/RankCard"

const GOLD = "#D4AF37"
const PLATFORMS = ["youtube","tiktok","instagram","facebook","soundcloud"]

function authFetch(url, token, opts = {}) {
  return fetch(url, { ...opts, headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(opts.headers || {}) } })
}

export default function Dashboard() {
  const { token, API } = useAuth()
  const [user, setUser]       = useState(null)
  const [xpData, setXpData]   = useState(null)
  const [status, setStatus]   = useState(null)
  const [account, setAccount] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      authFetch(`${API}/users/me`, token).then(r => r.json()),
      authFetch(`${API}/paper/xp`, token).then(r => r.json()),
      authFetch(`${API}/rewards/status`, token).then(r => r.json()),
      authFetch(`${API}/paper/account`, token).then(r => r.json()),
    ]).then(([u, xp, s, acc]) => { setUser(u); setXpData(xp); setStatus(s); setAccount(acc) })
      .finally(() => setLoading(false))
  }, [token])

  if (loading) return <div style={{ color: "#555", padding: "4rem", textAlign: "center" }}>Loading the record...</div>

  const stats = [
    { label: "Discount",      value: `${status?.discount_pct || 0}%`,                          sub: "on all purchases" },
    { label: "Freebies",      value: status?.freebies_unlocked || 0,                            sub: "items unlocked" },
    { label: "Platforms",     value: `${status?.platforms_followed?.length || 0}/5`,            sub: "socials followed" },
    { label: "Paper balance", value: account ? `$${Math.round(account.balance).toLocaleString()}` : "—", sub: "paper trading" },
  ]

  return (
    <div>
      <RankCard xp={user?.xp || 0} rank={user?.observer_rank || "Novice Observer"} nextRank={status?.next_rank} xpToNext={status?.xp_to_next_rank} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: "1.5rem" }}>
        {stats.map(s => (
          <div key={s.label} style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "1rem" }}>
            <div style={{ color: "#555", fontSize: 11, textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>{s.label}</div>
            <div style={{ color: GOLD, fontSize: 24, fontWeight: 700 }}>{s.value}</div>
            <div style={{ color: "#444", fontSize: 11, marginTop: 2 }}>{s.sub}</div>
          </div>
        ))}
      </div>

      <div style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "1.25rem", marginBottom: "1.5rem" }}>
        <div style={{ color: "#888", fontSize: 12, textTransform: "uppercase", letterSpacing: 1, marginBottom: 10 }}>Social platforms — +25 XP each, +50 bonus for all 5</div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {PLATFORMS.map(p => {
            const followed = status?.platforms_followed?.includes(p)
            return (
              <div key={p} style={{ padding: "6px 14px", borderRadius: 20, fontSize: 12, background: followed ? "#1a1a0a" : "transparent", color: followed ? GOLD : "#444", border: `1px solid ${followed ? GOLD : "#222"}` }}>
                {followed ? "✓" : "○"} {p.charAt(0).toUpperCase() + p.slice(1)}
              </div>
            )
          })}
        </div>
        {status?.platforms_remaining?.length > 0 && (
          <div style={{ color: "#444", fontSize: 12, marginTop: 10 }}>Go to Rewards to record follows and claim XP.</div>
        )}
      </div>

      <div style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "1.25rem" }}>
        <div style={{ color: "#888", fontSize: 12, textTransform: "uppercase", letterSpacing: 1, marginBottom: 12 }}>Recent XP events</div>
        {xpData?.recent_events?.length === 0 && <div style={{ color: "#333", fontSize: 13 }}>No events yet. Follow a social to start.</div>}
        {xpData?.recent_events?.map((e, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: i < xpData.recent_events.length - 1 ? "1px solid #111" : "none" }}>
            <div>
              <div style={{ color: "#ccc", fontSize: 13 }}>{e.description}</div>
              <div style={{ color: "#444", fontSize: 11 }}>{e.type}</div>
            </div>
            <div style={{ color: GOLD, fontSize: 14, fontWeight: 700 }}>+{e.xp} XP</div>
          </div>
        ))}
      </div>
    </div>
  )
}
