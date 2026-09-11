import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import styles from "../styles/shared.module.css";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    my_username: "", phone_number: "", my_email: "",
    first_name: "", last_name: "", password: "",
  });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await apiFetch("/auth/register/", { method: "POST", body: form });
      navigate("/verify", { state: form });
    } catch (err) {
      setError(Object.values(err.data || {})[0]?.[0] || "فرم خود را بازبینی کنید");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={styles.authPage}>
      <h1>ثبت‌نام</h1>
      {error && <p className={styles.error}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input name="my_username" placeholder="نام کاربری" value={form.my_username} onChange={handleChange} required />
        <input name="first_name" placeholder="نام" value={form.first_name} onChange={handleChange} required />
        <input name="last_name" placeholder="نام خانوادگی" value={form.last_name} onChange={handleChange} required />
        <input name="phone_number" placeholder="شماره تلفن" value={form.phone_number} onChange={handleChange} required maxLength={11} />
        <input name="my_email" type="email" placeholder="ایمیل" value={form.my_email} onChange={handleChange} required />
        <input name="password" type="password" placeholder="رمز عبور" value={form.password} onChange={handleChange} required />
        <button type="submit" disabled={submitting}>ارسال کد تایید</button>
      </form>
    </div>
  );
}
