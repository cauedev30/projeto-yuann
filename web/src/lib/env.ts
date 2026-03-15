type ClientEnv = {
  NEXT_PUBLIC_API_URL: string;
};

export function loadClientEnv(input: Partial<ClientEnv>): ClientEnv {
  const apiUrl = input.NEXT_PUBLIC_API_URL?.trim();

  if (!apiUrl) {
    throw new Error("NEXT_PUBLIC_API_URL is required");
  }

  return {
    NEXT_PUBLIC_API_URL: apiUrl,
  };
}

export function getClientEnv(): ClientEnv {
  return loadClientEnv({
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  });
}
