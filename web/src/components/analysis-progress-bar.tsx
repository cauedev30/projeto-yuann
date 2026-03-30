"use client";

import React from "react";

import type { AnalysisProgress } from "@/lib/hooks/use-analysis-stream";

type AnalysisProgressBarProps = {
  progress: AnalysisProgress | null;
  isStreaming: boolean;
  isComplete: boolean;
  error: string | null;
};

export function AnalysisProgressBar({
  progress,
  isStreaming,
  isComplete,
  error,
}: AnalysisProgressBarProps) {
  if (!progress && !isStreaming && !isComplete && !error) {
    return null;
  }

  const getProgressPercentage = () => {
    if (!progress) return 0;
    switch (progress.stage) {
      case "started":
        return 10;
      case "chunking":
        return 30;
      case "analyzing":
        return 60;
      case "completed":
        return 100;
      case "error":
        return 0;
      default:
        return 0;
    }
  };

  const getStatusColor = () => {
    if (error) return "bg-red-500";
    if (isComplete) return "bg-green-500";
    return "bg-cyan-500";
  };

  return (
    <div className="analysis-progress">
      <div className="progress-header">
        <span className="progress-label">
          {error ? "Erro" : isComplete ? "Análise concluída" : "Analisando..."}
        </span>
      </div>

      <div className="progress-bar-container">
        <div
          className={`progress-bar ${getStatusColor()}`}
          style={{ width: `${getProgressPercentage()}%` }}
        />
      </div>

      <p className="progress-message">
        {error || progress?.message || "Iniciando..."}
      </p>

      {isComplete && progress?.findingsCount !== undefined && (
        <p className="findings-count">
          {progress.findingsCount} achados identificados
        </p>
      )}

      <style jsx>{`
        .analysis-progress {
          padding: 1rem;
          background: var(--surface-secondary, #1e293b);
          border-radius: 8px;
          margin: 1rem 0;
        }

        .progress-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .progress-label {
          font-weight: 500;
          color: var(--text-primary, #fff);
        }

        .progress-bar-container {
          height: 8px;
          background: var(--surface-tertiary, #334155);
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-bar {
          height: 100%;
          transition: width 0.3s ease;
          border-radius: 4px;
        }

        .progress-message {
          margin-top: 0.5rem;
          font-size: 0.875rem;
          color: var(--text-secondary, #94a3b8);
        }

        .findings-count {
          margin-top: 0.25rem;
          font-size: 0.875rem;
          color: var(--text-secondary, #94a3b8);
        }
      `}</style>
    </div>
  );
}
