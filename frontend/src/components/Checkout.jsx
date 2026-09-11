import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import styles from "../styles/shared.module.css";

export default function Checkout() {
  const { state: pending } = useLocation();
  const navigate = useNavigate();
  const [receipt, setReceipt] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (!pending) {
    navigate("/");
    return null;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!receipt) {
      setError("لطفاً تصویر رسید را بارگذاری کنید.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await apiFetch("/reservations/", {
        method: "POST",
        isMultipart: true,
        body: {
          room: pending.room_id,
          phone_number: pending.phone_number,
          first_name: pending.first_name,
          last_name: pending.last_name,
          reservation_date_start: pending.reservation_date_start,
          reservation_date_end: pending.reservation_date_end,
          receipt,
        },
      });
      navigate("/reservation-success");
    } catch (err) {
      setError(err.data?.detail || "خطایی در ثبت رزرو رخ داد");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1>تکمیل رزرو و پرداخت</h1>
      <ul>
        <li>نام: {pending.first_name} {pending.last_name}</li>
        <li>تلفن: {pending.phone_number}</li>
        <li>از {pending.reservation_date_start} تا {pending.reservation_date_end}</li>
      </ul>
      {error && <p className={styles.error}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          تصویر رسید پرداخت:
          <input type="file" accept="image/*" onChange={(e) => setReceipt(e.target.files[0])} required />
        </label>
        <button type="submit" disabled={submitting}>ثبت نهایی رزرو</button>
      </form>
    </div>
  );
}
