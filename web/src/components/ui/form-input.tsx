import React, { type InputHTMLAttributes } from "react";

import styles from "./ui-primitives.module.css";

type FormInputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
};

export function FormInput({ label, id, ...rest }: FormInputProps) {
  const inputId = id ?? `form-input-${label.toLowerCase().replace(/\s+/g, "-")}`;

  return (
    <div className={styles.formField}>
      <label className={styles.formLabel} htmlFor={inputId}>
        {label}
      </label>
      <input className={styles.formInput} id={inputId} {...rest} />
    </div>
  );
}
