import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../context/AuthContext";
import styles from "../styles/shared.module.css";

import DatePicker from "react-multi-date-picker";
import DateObject from "react-date-object";
import persian from "react-date-object/calendars/persian";
import persian_fa from "react-date-object/locales/persian_fa";

// The picker's locale (persian_fa) renders digits in Farsi script
// (۱۴۰۴/۰۷/۰۱), but the backend sends/expects plain Latin-digit strings
// (1404/07/01, from Python's jdatetime). date.format() would silently
// produce Farsi digits and never match — so build the key manually from
// the raw numeric year/month/day instead, which is always Latin digits.
function toJalaliKey(date) {
  const y = date.year;
  const m = String(date.month.number).padStart(2, "0");
  const d = String(date.day).padStart(2, "0");
  return `${y}/${m}/${d}`;
}

function toJalaliKeyFromTimestamp(ms) {
  const d = new DateObject({ date: new Date(ms), calendar: persian, locale: persian_fa });
  return toJalaliKey(d);
}

// Checks every day strictly between start and end against reservedDays.
// Uses a numeric day-count (via real elapsed milliseconds) as the loop
// bound instead of comparing formatted date strings — the previous
// version looped `cursor = cursor.add(1, "day")` until it string-matched
// `end`, which never terminates (freezing the tab) if end isn't strictly
// after start, e.g. equal dates or a reversed pair. A bounded numeric
// loop can't hang no matter what order the two dates come in.
function rangeOverlapsReserved(start, end, reservedDays) {
  const startMs = start.toDate().getTime();
  const endMs = end.toDate().getTime();
  const diffDays = Math.round((endMs - startMs) / 86400000);
  if (diffDays <= 0) return false; // same day or reversed — not a valid range at all, handled elsewhere
  for (let i = 1; i < diffDays; i++) {
    if (reservedDays.includes(toJalaliKeyFromTimestamp(startMs + i * 86400000))) return true;
  }
  return false;
}

export default function ReservationForm() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [room, setRoom] = useState(null);
  const [reservedDays, setReservedDays] = useState([]);
  const [dateRange, setDateRange] = useState([]); // [DateObject, DateObject] once both picked
  const [form, setForm] = useState({ phone_number: "", first_name: "", last_name: "" });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    apiFetch(`/rooms/${roomId}/`).then(setRoom);
    apiFetch(`/rooms/${roomId}/reserved-days/`).then((d) => setReservedDays(d.reserved_days));
  }, [roomId, user, navigate]);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  // Only disables direct clicks on a reserved day — doesn't touch the
  // picker's own selection state, so it can't interfere with normal
  // two-click range picking.
  function mapDays({ date }) {
    if (reservedDays.includes(toJalaliKey(date))) {
      return {
        disabled: true,
        style: { backgroundColor: "#a8402c", color: "#fff", borderRadius: "50%" },
      };
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (dateRange.length < 2) {
      setError("لطفاً تاریخ شروع و پایان اقامت را انتخاب کنید.");
      return;
    }
    if (rangeOverlapsReserved(dateRange[0], dateRange[1], reservedDays)) {
      setError("این بازه شامل روز‌های رزرو شده است. لطفاً بازه دیگری انتخاب کنید.");
      return;
    }

    setSubmitting(true);
    try {
      const body = {
        room_id: Number(roomId),
        ...form,
        reservation_date_start: toJalaliKey(dateRange[0]),
        reservation_date_end: toJalaliKey(dateRange[1]),
      };
      const validated = await apiFetch("/reservations/validate/", { method: "POST", body });
      navigate("/checkout", { state: validated });
    } catch (err) {
      setError(err.data?.detail || Object.values(err.data || {})[0] || "خطایی رخ داد");
    } finally {
      setSubmitting(false);
    }
  }

  if (!room) return <p>در حال بارگذاری...</p>;

  return (
    <div>
      <h1>رزرو {room.name}</h1>
      {error && <p className={styles.error}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <input name="first_name" placeholder="نام" value={form.first_name} onChange={handleChange} required />
        <input name="last_name" placeholder="نام خانوادگی" value={form.last_name} onChange={handleChange} required />
        <input name="phone_number" placeholder="شماره تلفن" value={form.phone_number} onChange={handleChange} required maxLength={11} />

        <label>
          بازه اقامت (شروع - پایان)
          <DatePicker
            range
            calendar={persian}
            locale={persian_fa}
            format="YYYY/MM/DD"
            value={dateRange}
            onChange={setDateRange}
            mapDays={mapDays}
            minDate={new Date()}
            numberOfMonths={1}
            placeholder="انتخاب تاریخ"
          />
        </label>

        <button type="submit" disabled={submitting}>ادامه به پرداخت</button>
      </form>
    </div>
  );
}
