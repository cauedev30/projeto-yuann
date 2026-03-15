type ContractDetailPageProps = {
  params: Promise<{ contractId: string }>;
};

export default async function ContractDetailPage({ params }: ContractDetailPageProps) {
  const { contractId } = await params;

  return (
    <main>
      <p>Detalhe do contrato</p>
      <h1>{contractId}</h1>
      <p>A timeline detalhada e os findings persistidos entram na proxima iteracao.</p>
    </main>
  );
}
