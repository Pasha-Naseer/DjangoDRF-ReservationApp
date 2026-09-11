import { BrowserRouter, Routes, Route, Link, NavLink } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import navStyles from "./styles/nav.module.css";

import Home from "./components/Home";
import RoomDetail from "./components/RoomDetail";
import ReservationForm from "./components/ReservationForm";
import Checkout from "./components/Checkout";
import Login from "./components/Login";
import Register from "./components/Register";
import VerifyCode from "./components/VerifyCode";
import ReservationStatus from "./components/ReservationStatus";
import About from "./components/About";
import { WeblogList, WeblogDetail } from "./components/Weblog";

function ReservationSuccess() {
  return <h1>رزرو شما با موفقیت ثبت شد ✅</h1>;
}

function navLinkClass({ isActive }) {
  return isActive ? `${navStyles.link} ${navStyles.linkActive}` : navStyles.link;
}

function Nav() {
  const { user, logout } = useAuth();
  return (
    <nav className={navStyles.nav}>
      <Link to="/" className={navStyles.brand}>
        <span className={navStyles.brandMark} />
        سهند
      </Link>

      <div className={navStyles.links}>
        <NavLink to="/" end className={navLinkClass}>خانه</NavLink>
        <NavLink to="/weblog" className={navLinkClass}>وبلاگ</NavLink>
        <NavLink to="/about" className={navLinkClass}>درباره ما</NavLink>
        {user && (
          <NavLink to="/my-reservations" className={navLinkClass}>رزروهای من</NavLink>
        )}
      </div>

      <div className={navStyles.actions}>
        {user ? (
          <button className={navStyles.logoutBtn} onClick={logout}>خروج</button>
        ) : (
          <>
            <Link to="/login" className={navStyles.ghostLink}>ورود</Link>
            <Link to="/register" className={navStyles.primaryLink}>ثبت‌نام</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Nav />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/rooms/:roomId" element={<RoomDetail />} />
          <Route path="/rooms/:roomId/reserve" element={<ReservationForm />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/reservation-success" element={<ReservationSuccess />} />
          <Route path="/my-reservations" element={<ReservationStatus />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify" element={<VerifyCode />} />
          <Route path="/weblog" element={<WeblogList />} />
          <Route path="/weblog/:weblogId" element={<WeblogDetail />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
