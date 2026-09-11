import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiFetch } from "../api/client";
import styles from "../styles/shared.module.css";

export function WeblogList() {
  const [weblogs, setWeblogs] = useState(null);

  useEffect(() => {
    apiFetch("/weblogs/").then((data) => setWeblogs(data.results ?? data));
  }, []);

  if (!weblogs) return <p>در حال بارگذاری...</p>;

  return (
    <div>
      <h1>وبلاگ</h1>
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

export function WeblogDetail() {
  const { weblogId } = useParams();
  const [weblog, setWeblog] = useState(null);

  useEffect(() => {
    apiFetch(`/weblogs/${weblogId}/`).then(setWeblog);
  }, [weblogId]);

  if (!weblog) return <p>در حال بارگذاری...</p>;

  return (
    <article>
      <h1>{weblog.title}</h1>
      {weblog.blog_image && <img src={weblog.blog_image} alt={weblog.title} className={styles.galleryImage} />}
      <div dangerouslySetInnerHTML={{ __html: weblog.body }} />
    </article>
  );
}
