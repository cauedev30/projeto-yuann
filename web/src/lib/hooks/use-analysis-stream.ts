"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { getClientEnv } from "@/lib/env";
import { contractKeys } from "./use-contracts";

export type AnalysisStage = "started" | "chunking" | "analyzing" | "completed" | "error";

export type AnalysisProgress = {
  stage: AnalysisStage;
  message: string;
  total?: number;
  riskScore?: number;
  findingsCount?: number;
};

export type UseAnalysisStreamResult = {
  progress: AnalysisProgress | null;
  isStreaming: boolean;
  isComplete: boolean;
  error: string | null;
  startAnalysis: () => void;
  reset: () => void;
};

export function useAnalysisStream(contractId: string): UseAnalysisStreamResult {
  const queryClient = useQueryClient();
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const cleanup = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    cleanup();
    setProgress(null);
    setIsStreaming(false);
    setIsComplete(false);
    setError(null);
  }, [cleanup]);

  const startAnalysis = useCallback(() => {
    reset();
    setIsStreaming(true);

    const { NEXT_PUBLIC_API_URL } = getClientEnv();
    const url = `${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/analyze-stream`;

    // Note: EventSource doesn't support custom headers.
    // For authenticated SSE, we'd need to use fetch with ReadableStream
    // or pass token in query params. For now, assuming backend handles auth.
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as {
          stage: AnalysisStage;
          message: string;
          total?: number;
          risk_score?: number;
          findings_count?: number;
        };

        const progressUpdate: AnalysisProgress = {
          stage: data.stage,
          message: data.message,
          total: data.total,
          riskScore: data.risk_score,
          findingsCount: data.findings_count,
        };

        setProgress(progressUpdate);

        if (data.stage === "completed") {
          setIsComplete(true);
          setIsStreaming(false);
          cleanup();
          
          // Invalidate contract queries to fetch updated analysis
          queryClient.invalidateQueries({ queryKey: contractKeys.detail(contractId) });
          queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
        } else if (data.stage === "error") {
          setError(data.message);
          setIsStreaming(false);
          cleanup();
        }
      } catch (err) {
        console.error("Error parsing SSE message:", err);
      }
    };

    eventSource.onerror = () => {
      setError("Conexão perdida com o servidor.");
      setIsStreaming(false);
      cleanup();
    };
  }, [contractId, cleanup, reset, queryClient]);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    progress,
    isStreaming,
    isComplete,
    error,
    startAnalysis,
    reset,
  };
}
