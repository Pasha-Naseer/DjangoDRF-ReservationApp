import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function ReservationStatus() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [reservations, setReservations] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    apiFetch("/reservations/mine/").then(setReservations);
  }, [user, navigate]);

  if (!reservations) return <p>در حال بارگذاری...</p>;

  return (
    <div>
      <h1>رزروهای من</h1>
      {reservations.length === 0 && <p>رزروی ثبت نشده است.</p>}
      <table>
        <thead>
          <tr><th>اتاق</th><th>از</th><th>تا</th><th>مبلغ کل</th><th>وضعیت</th></tr>
        </thead>
        <tbody>
          {reservations.map((r) => (
            <tr key={r.id}>
              <td>{r.room.name}</td>
              <td>{r.reservation_date_start_jalali}</td>
              <td>{r.reservation_date_end_jalali}</td>
              <td>{r.total_price} تومان</td>
              <td>{r.status_display}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
