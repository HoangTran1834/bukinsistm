import { useState } from "react";
import "./App.css";
import BookingList from "./components/BookingList";
import LoginForm from "./components/LoginForm";
import Profile from "./components/Profile";
import SignupForm from "./components/SignupForm";

function App() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token")
  );
  const [showSignup, setShowSignup] = useState(false);

  const handleLogin = (tk: string) => {
    setToken(tk);
    localStorage.setItem("token", tk);
  };
  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem("token");
  };

  if (!token) {
    return (
      <div style={{ maxWidth: 400, margin: "40px auto" }}>
        {showSignup ? (
          <>
            <SignupForm onSignup={() => setShowSignup(false)} />
            <button onClick={() => setShowSignup(false)}>
              Đã có tài khoản? Đăng nhập
            </button>
          </>
        ) : (
          <>
            <LoginForm onLogin={handleLogin} />
            <button onClick={() => setShowSignup(true)}>
              Chưa có tài khoản? Đăng ký
            </button>
          </>
        )}
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 600, margin: "40px auto" }}>
      <button onClick={handleLogout} style={{ float: "right" }}>
        Đăng xuất
      </button>
      <Profile token={token} />
      <BookingList token={token} />
    </div>
  );
}

export default App;
