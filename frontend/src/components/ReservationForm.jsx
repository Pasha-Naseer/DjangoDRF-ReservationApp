import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../context/AuthContext";
import styles from "../styles/shared.module.css";

import DatePicker from "react-multi-date-picker";
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

// Returns true if any day strictly between start and end is already reserved.
function rangeHitsReservedDay(start, end, reservedDays) {
  let cursor = start.add(1, "day");
  while (toJalaliKey(cursor) !== toJalaliKey(end)) {
    if (reservedDays.includes(toJalaliKey(cursor))) return true;
    cursor = cursor.add(1, "day");
  }
  return false;
}

// Number of nights between two DateObjects, calendar-agnostic (just real
// elapsed days), which is what total_price() on the backend charges for.
function nightsBetween(start, end) {
  const ms = end.toDate().getTime() - start.toDate().getTime();
  return Math.round(ms / 86400000);
}

export default function ReservationForm() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [room, setRoom] = useState(null);
  const [reservedDays, setReservedDays] = useState([]);
  const [dateRange, setDateRange] = useState([]); // [DateObject, DateObject] once both picked
  const [pickerKey, setPickerKey] = useState(0); // bumped to force a clean remount on rejection
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

  function rejectSelection(message) {
    setError(message);
    setDateRange([]);
    // The picker keeps some click-progress state internally that isn't
    // fully driven by the `value` prop, so resetting value alone can leave
    // a reserved day looking "selected" instead of red. Changing `key`
    // forces React to tear down and recreate the picker from scratch,
    // guaranteeing a clean visual reset.
    setPickerKey((k) => k + 1);
  }

  function handleRangeChange(value) {
    if (value.length === 2 && rangeHitsReservedDay(value[0], value[1], reservedDays)) {
      rejectSelection("این بازه شامل روز‌های رزرو شده است. لطفاً بازه دیگری انتخاب کنید.");
      return;
    }
    setError(null);
    setDateRange(value);
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  // inline `style` (not just a CSS class) is used because it can't lose a
  // specificity fight with the library's own built-in day styling.
  function mapDays({ date }) {
    if (reservedDays.includes(toJalaliKey(date))) {
      return {
        disabled: true,
        style: {
          backgroundColor: "#a8402c",
          color: "#fff",
          borderRadius: "50%",
        },
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

  const nights = dateRange.length === 2 ? nightsBetween(dateRange[0], dateRange[1]) : 0;
  const nightlyRate = room.has_discount ? room.price_with_discount : Number(room.price_per_night);
  const totalPrice = nights * nightlyRate;

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
            key={pickerKey}
            range
            calendar={persian}
            locale={persian_fa}
            format="YYYY/MM/DD"
            value={dateRange}
            onChange={handleRangeChange}
            mapDays={mapDays}
            minDate={new Date()}
            numberOfMonths={1}
            placeholder="انتخاب تاریخ"
          />
        </label>

        {nights > 0 && (
          <p className={styles.hint}>
            {nights} شب × {nightlyRate.toLocaleString("en-US")} تومان ={" "}
            <strong>{totalPrice.toLocaleString("en-US")} تومان</strong>
          </p>
        )}

        <button type="submit" disabled={submitting}>ادامه به پرداخت</button>
      </form>
    </div>
  );
}
