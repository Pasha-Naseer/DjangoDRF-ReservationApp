import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import styles from "../styles/shared.module.css";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(form.username, form.password);
      navigate("/");
    } catch (err) {
      setError(err.data?.non_field_errors?.[0] || "خطایی در حین ورود به حساب رخ داد");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={styles.authPage}>
      <h1>ورود</h1>
      {error && <p className={styles.error}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          placeholder="نام کاربری"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          required
        />
        <input
          type="password"
          placeholder="رمز عبور"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />
        <button type="submit" disabled={submitting}>ورود</button>
      </form>
      <p>حساب کاربری ندارید؟ <Link to="/register">ثبت‌نام</Link></p>
    </div>
  );
}
