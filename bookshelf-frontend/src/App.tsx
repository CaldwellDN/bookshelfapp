import { BrowserRouter, Routes, Route, Link } from "react-router-dom"
import Login from "./pages/Login"
import Library from "./pages/Library"
import Reader from "./pages/Reader"
import ProtectedRoute from "./ProtectedRoute"
import UserMenu from "./components/UserMenu"

function App() {
  return (
    <div>
    <BrowserRouter>
      <nav
        style={{
          display: "flex",
          gap: "1rem",
          padding: "1rem",
          borderBottom: "1px solid #ddd",
        }}
      >
        <Link to="/">Login</Link>
        <Link to="/library">Library</Link>
        <Link to="/reader/1">Reader</Link>
        <UserMenu />
      </nav>

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/library" element={
            <ProtectedRoute>
                <Library />
            </ProtectedRoute>
        }/>
        <Route path="/reader/:bookId" element={
            <ProtectedRoute>
                <Reader />
            </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
    </div>
  )
}

export default App
