import { useAuth } from "../App"

const GOLD = "#D4AF37"

export default function Nav({ page, setPage, logout }) {
  const tabs = [
    { key: "dashboard", label: "Dashboard" },
    { key: "rewards",   label: "Rewards" },
    { key: "freebies",  label: "Freebies" },
  ]
  return (
    <nav style={{ borderBottom: "1px solid #222", padding: "1rem 2rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <span style={{ color: GOLD, fontWeight: 700, fontSize: 18, letterSpacing: 2 }}>👁️ FRACTURE VAULTS</span>
      <div style={{ display: "flex", gap: 8 }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setPage(t.key)} style={{
            background: page === t.key ? GOLD : "transparent",
            color: page === t.key ? "#000" : "#888",
            border: `1px solid ${page === t.key ? GOLD : "#333"}`,
            borderRadius: 4, padding: "6px 16px", cursor: "pointer", fontSize: 13,
          }}>{t.label}</button>
        ))}
        <button onClick={logout} style={{
          background: "transparent", color: "#555", border: "1px solid #333",
          borderRadius: 4, padding: "6px 16px", cursor: "pointer", fontSize: 13,
        }}>Sign out</button>
      </div>
    </nav>
  )
}
