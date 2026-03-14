const GOLD = "#D4AF37"

const RANKS = [
  { name: "Novice Observer",    xp: 0 },
  { name: "The Watcher",        xp: 100 },
  { name: "Keeper of Signals",  xp: 500 },
  { name: "Fracture Reader",    xp: 1500 },
  { name: "Inner Marches Guard",xp: 3000 },
  { name: "Elder of the Vault", xp: 6000 },
  { name: "The Unseen",         xp: 10000 },
]

export default function RankCard({ xp = 0, rank = "Novice Observer", nextRank, xpToNext }) {
  const current = RANKS.find(r => r.name === rank) || RANKS[0]
  const next = RANKS.find(r => r.name === nextRank)
  const pct = next
    ? Math.min(100, Math.round(((xp - current.xp) / (next.xp - current.xp)) * 100))
    : 100

  return (
    <div style={{ background: "#0d0d0d", border: "1px solid #222", borderRadius: 8, padding: "1.5rem", marginBottom: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div>
          <div style={{ color: "#555", fontSize: 11, textTransform: "uppercase", letterSpacing: 2, marginBottom: 4 }}>Observer rank</div>
          <div style={{ color: GOLD, fontSize: 22, fontWeight: 700 }}>{rank}</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ color: "#555", fontSize: 11, textTransform: "uppercase", letterSpacing: 2, marginBottom: 4 }}>Total XP</div>
          <div style={{ color: "#fff", fontSize: 22, fontWeight: 700 }}>{xp.toLocaleString()}</div>
        </div>
      </div>
      <div style={{ background: "#1a1a1a", borderRadius: 4, height: 6, marginBottom: 6 }}>
        <div style={{ background: GOLD, borderRadius: 4, height: 6, width: `${pct}%`, transition: "width 0.6s ease" }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#555" }}>
        <span>{rank}</span>
        <span>{next ? `${xpToNext?.toLocaleString()} XP to ${nextRank}` : "Max rank achieved"}</span>
      </div>
      <div style={{ display: "flex", gap: 4, marginTop: 16, flexWrap: "wrap" }}>
        {RANKS.map(r => {
          const unlocked = xp >= r.xp
          const active = r.name === rank
          return (
            <div key={r.name} style={{
              fontSize: 10, padding: "3px 8px", borderRadius: 20,
              background: active ? GOLD : unlocked ? "#1a1a1a" : "transparent",
              color: active ? "#000" : unlocked ? "#888" : "#333",
              border: `1px solid ${active ? GOLD : unlocked ? "#333" : "#1a1a1a"}`,
              fontWeight: active ? 700 : 400,
            }}>{r.name}</div>
          )
        })}
      </div>
    </div>
  )
}
