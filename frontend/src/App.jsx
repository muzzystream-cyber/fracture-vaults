import { useState, useEffect, createContext, useContext } from "react"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Dashboard from "./pages/Dashboard"
import Rewards from "./pages/Rewards"
import Freebies from "./pages/Freebies"
import Nav from "./components/Nav"

const API = import.meta.env.VITE_API_URL || "https://web-production-c769.up.railway.app/api/v1"

export const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("fv_token"))
  const [page, setPage] = useState("dashboard")

  useEffect(() => {
    if (token) localStorage.setItem("fv_token", token)
    else localStorage.removeItem("fv_token")
  }, [token])

  const logout = () => { setToken(null); setPage("dashboard") }

  if (!token) {
    return (
      <AuthContext.Provider value={{ token, setToken, API }}>
        <div style={{ minHeight: "100vh", background: "#000", display: "flex", alignItems: "center", justifyContent: "center" }}>
          {page === "register"
            ? <Register onSwitch={() => setPage("login")} />
            : <Login onSwitch={() => setPage("register")} />
          }
        </div>
      </AuthContext.Provider>
    )
  }

  return (
    <AuthContext.Provider value={{ token, setToken, API, logout }}>
      <div style={{ minHeight: "100vh", background: "#000", color: "#fff", fontFamily: "Georgia, serif" }}>
        <Nav page={page} setPage={setPage} logout={logout} />
        <main style={{ maxWidth: 960, margin: "0 auto", padding: "2rem 1rem" }}>
          {page === "dashboard" && <Dashboard />}
          {page === "rewards"   && <Rewards />}
          {page === "freebies"  && <Freebies />}
        </main>
      </div>
    </AuthContext.Provider>
  )
}
