import styles from "./page.module.css";
import ImageUploader from "./imageUploader";
export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.titleContainer}>
        <h1 className={styles.title}>Photo2Vangogh</h1>
        <p>Transform your photo to vangogh like style painting</p>
      </div>
      <ImageUploader />
    </main>
  );
}
