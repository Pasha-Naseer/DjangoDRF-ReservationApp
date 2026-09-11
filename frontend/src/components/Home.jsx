import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import styles from "../styles/shared.module.css";

export default function Home() {
  const [rooms, setRooms] = useState([]);
  const [weblogs, setWeblogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch("/rooms/"),
      apiFetch("/weblogs/latest/"),
    ]).then(([roomList, latestWeblogs]) => {
      setRooms(roomList.results ?? roomList);
      setWeblogs(latestWeblogs);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <p>در حال بارگذاری...</p>;

  return (
    <div>
      <h1>اتاق‌ها</h1>
      <div className={styles.grid}>
        {rooms.map((room) => (
          <Link to={`/rooms/${room.id}`} key={room.id} className={styles.card}>
            <div className={styles.imageWrap}>
              {room.has_discount && <span className={styles.badge}>%{room.discount} تخفیف</span>}
              {room.images?.[0] && <img src={room.images[0]} alt={room.name} className={styles.cardImage} />}
            </div>
            <div className={styles.cardBody}>
              <h3 className={styles.cardTitle}>{room.name}</h3>
              <div className={styles.price}>
                {room.has_discount ? (
                  <>
                    <span>{room.price_with_discount} تومان</span>
                    <span className={styles.strike}>{room.price_per_night}</span>
                  </>
                ) : (
                  <span>{room.price_per_night} تومان / شب</span>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>

      <h2>آخرین مطالب وبلاگ</h2>
      <div className={styles.grid}>
        {weblogs.map((w) => (
          <Link to={`/weblog/${w.id}`} key={w.id} className={styles.card}>
            <div className={styles.imageWrap}>
              {w.blog_image && <img src={w.blog_image} alt={w.title} className={styles.cardImage} />}
            </div>
            <div className={styles.cardBody}>
              <h3 className={styles.cardTitle}>{w.title}</h3>
              <p className={styles.cardText}>{w.summary}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
