import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import styles from "../styles/shared.module.css";

export default function RoomDetail() {
  const { roomId } = useParams();
  const [room, setRoom] = useState(null);
  const [activeImage, setActiveImage] = useState(0);

  useEffect(() => {
    setActiveImage(0); // reset to the first image whenever the room changes
    apiFetch(`/rooms/${roomId}/`).then(setRoom);
  }, [roomId]);

  if (!room) return <p>در حال بارگذاری...</p>;

  const images = room.images;

  function showPrev() {
    setActiveImage((i) => (i === 0 ? images.length - 1 : i - 1));
  }
  function showNext() {
    setActiveImage((i) => (i === images.length - 1 ? 0 : i + 1));
  }

  return (
    <div>
      <h1>{room.name}</h1>

      {images.length > 0 && (
        <div className={styles.carousel}>
          <img src={images[activeImage]} alt={room.name} className={styles.carouselImage} />

          {images.length > 1 && (
            <>
              <button type="button" className={styles.carouselPrev} onClick={showPrev} aria-label="تصویر قبلی">
                ‹
              </button>
              <button type="button" className={styles.carouselNext} onClick={showNext} aria-label="تصویر بعدی">
                ›
              </button>

              <div className={styles.dots}>
                {images.map((src, i) => (
                  <button
                    type="button"
                    key={src}
                    className={i === activeImage ? `${styles.dot} ${styles.dotActive}` : styles.dot}
                    onClick={() => setActiveImage(i)}
                    aria-label={`تصویر ${i + 1}`}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      )}

      <p>{room.description}</p>
      {room.has_discount ? (
        <p><s className={styles.strike}>{room.price_per_night}</s> {room.price_with_discount} تومان / شب</p>
      ) : (
        <p>{room.price_per_night} تومان / شب</p>
      )}
      <Link to={`/rooms/${room.id}/reserve`} className="btn">رزرو این اتاق</Link>
    </div>
  );
}
