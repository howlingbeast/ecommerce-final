// src/components/BannerCarousel/BannerCarousel.tsx
import styles from './BannerCarousel.module.css';
import bgVideo from '../../assets/gojo-bg.mp4';

const BannerCarousel = () => {
  const handleShopNow = () => {
    const el = document.querySelector('[data-product-section]');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className={styles.hero}>
      {/* 五条悟 视频背景 */}
      <video className={styles.bgVideo} autoPlay muted loop playsInline>
        <source src={bgVideo} type="video/mp4" />
      </video>
      <div className={styles.overlay} />

      <div className={styles.heroInner}>
        <div className={styles.heroContent}>
          <span className={styles.badge}>✨ 新品发售</span>
          <h2 className={styles.title}>五条悟 · 领域展开</h2>
          <p className={styles.subtitle}>「天上天下，唯我独尊」满199减50</p>
          <div className={styles.heroCta} onClick={handleShopNow}>
            <span className={styles.ctaText}>✨ 立即选购</span>
            <span className={styles.ctaArrow}>→</span>
          </div>
        </div>
        <div className={styles.heroVisual}>
          <div className={styles.floatingIcon}>🔮</div>
          <div className={styles.floatingIcon2}>⚡</div>
          <div className={styles.floatingIcon3}>∞</div>
        </div>
      </div>
    </div>
  );
};

export default BannerCarousel;
