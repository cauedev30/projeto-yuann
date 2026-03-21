"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listContracts,
  getContractDetail,
  uploadContract,
  deleteContract,
  updateContract,
  analyzeContract,
  generateCorrectedContract,
  type CorrectedContractResponse,
} from "@/lib/api/contracts";
import type {
  ContractListResponse,
  ContractDetail,
  ContractUploadResult,
  ContractUploadInput,
} from "@/entities/contracts/model";

export const contractKeys = {
  all: ["contracts"] as const,
  lists: () => [...contractKeys.all, "list"] as const,
  list: (filters?: Record<string, unknown>) => [...contractKeys.lists(), filters] as const,
  details: () => [...contractKeys.all, "detail"] as const,
  detail: (id: string) => [...contractKeys.details(), id] as const,
};

export function useContracts() {
  return useQuery<ContractListResponse>({
    queryKey: contractKeys.list(),
    queryFn: () => listContracts(),
  });
}

export function useContract(contractId: string) {
  return useQuery<ContractDetail>({
    queryKey: contractKeys.detail(contractId),
    queryFn: () => getContractDetail(contractId),
    enabled: !!contractId,
  });
}

export function useUploadContract() {
  const queryClient = useQueryClient();

  return useMutation<ContractUploadResult, Error, ContractUploadInput>({
    mutationFn: (input) => uploadContract(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

export function useDeleteContract() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (contractId) => deleteContract(contractId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

export function useUpdateContract() {
  const queryClient = useQueryClient();

  return useMutation<
    ContractDetail,
    Error,
    {
      contractId: string;
      updates: Parameters<typeof updateContract>[1];
    }
  >({
    mutationFn: ({ contractId, updates }) => updateContract(contractId, updates),
    onSuccess: (data) => {
      queryClient.setQueryData(contractKeys.detail(data.contract.id), data);
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

export function useAnalyzeContract() {
  const queryClient = useQueryClient();

  return useMutation<ContractDetail, Error, string>({
    mutationFn: (contractId) => analyzeContract(contractId),
    onSuccess: (data) => {
      queryClient.setQueryData(contractKeys.detail(data.contract.id), data);
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

export function useGenerateCorrectedContract() {
  return useMutation<CorrectedContractResponse, Error, string>({
    mutationFn: (contractId) => generateCorrectedContract(contractId),
  });
}
