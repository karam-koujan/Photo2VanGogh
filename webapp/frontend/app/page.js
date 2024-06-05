import styles from "./page.module.css";
import ImageUploader from "./imageUploader";
export default function Home() {
  return (
    <>
      <h1>Image Uploader</h1>
      <main className={styles.main}>
        <ImageUploader />
      </main>
    </>
  );
}
