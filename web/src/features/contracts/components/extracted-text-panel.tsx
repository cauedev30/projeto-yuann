import React from "react";

import styles from "../screens/contracts-screen.module.css";

type ExtractedTextPanelProps = {
  text: string;
};

export function ExtractedTextPanel({ text }: ExtractedTextPanelProps) {
  return (
    <section className={`${styles.panel} ${styles.textPanel}`}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.panelEyebrow}>Base textual</p>
          <h2 className={styles.sectionTitle}>Texto extraido</h2>
        </div>
      </div>

      <pre className={styles.extractedText}>{text}</pre>
    </section>
  );
}
