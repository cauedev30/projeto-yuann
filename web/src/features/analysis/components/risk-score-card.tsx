type RiskScoreCardProps = {
  score: number;
  summary: string;
};

export function RiskScoreCard({ score, summary }: RiskScoreCardProps) {
  return (
    <section>
      <p>Score de risco</p>
      <strong>{score}</strong>
      <p>{summary}</p>
    </section>
  );
}
