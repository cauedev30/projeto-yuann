const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export type SearchResult = {
  contract_id: string;
  contract_title: string;
  chunk_type: string;
  chunk_text: string;
  similarity_score: number;
};

export type SearchResponse = {
  results: SearchResult[];
};

export async function searchContracts(
  query: string,
  limit: number = 10,
  min_similarity: number = 0.5,
): Promise<SearchResponse> {
  const res = await fetch(`${API_URL}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, limit, min_similarity }),
  });
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}