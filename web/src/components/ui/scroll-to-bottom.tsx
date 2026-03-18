"use client";

import React, { useCallback, useEffect, useState } from "react";

import styles from "./scroll-to-bottom.module.css";

const SCROLL_THRESHOLD = 200;

export function ScrollToBottom() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    function handleScroll() {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight;
      const clientHeight = document.documentElement.clientHeight;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

      setIsVisible(distanceFromBottom > SCROLL_THRESHOLD);
    }

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToBottom = useCallback(() => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: "smooth",
    });
  }, []);

  return (
    <button
      aria-label="Rolar para o final da pagina"
      className={`${styles.scrollButton} ${isVisible ? styles.visible : ""}`}
      onClick={scrollToBottom}
      type="button"
    >
      <svg
        aria-hidden="true"
        className={styles.chevron}
        fill="none"
        height="20"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2.5"
        viewBox="0 0 24 24"
        width="20"
      >
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </button>
  );
}
