import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { apiFetch, setTokens } from "../api/client";
import { useAuth } from "../context/AuthContext";
import styles from "../styles/shared.module.css";

export default function VerifyCode() {
  const { state: registrationInfo } = useLocation();
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [code, setCode] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (!registrationInfo) {
    navigate("/register");
    return null;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const data = await apiFetch("/auth/verify/", {
        method: "POST",
        body: { ...registrationInfo, code: Number(code) },
      });
      setTokens(data);
      setUser(data.user);
      navigate("/");
    } catch (err) {
      setError(err.data?.detail || "کد اشتباه است");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1>تایید شماره تلفن</h1>
      <p>کد ارسال شده به {registrationInfo.phone_number} را وارد کنید</p>
      {error && <p className={styles.error}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="کد ۴ رقمی" required maxLength={4} />
        <button type="submit" disabled={submitting}>تایید</button>
      </form>
    </div>
  );
}
