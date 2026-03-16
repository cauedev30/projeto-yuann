import { expect, test } from "@playwright/test";


function buildPdfWithText(text: string): Buffer {
  function assemblePdf(objects: Buffer[]): Buffer {
    const chunks: Buffer[] = [Buffer.from("%PDF-1.4\n", "ascii")];
    const offsets: number[] = [0];

    for (const [index, body] of objects.entries()) {
      offsets.push(Buffer.concat(chunks).length);
      chunks.push(Buffer.from(`${index + 1} 0 obj\n`, "ascii"));
      chunks.push(body);
      chunks.push(Buffer.from("\nendobj\n", "ascii"));
    }

    const body = Buffer.concat(chunks);
    const xrefOffset = body.length;
    const xref: Buffer[] = [Buffer.from(`xref\n0 ${objects.length + 1}\n`, "ascii")];
    xref.push(Buffer.from("0000000000 65535 f \n", "ascii"));
    for (const offset of offsets.slice(1)) {
      xref.push(Buffer.from(`${offset.toString().padStart(10, "0")} 00000 n \n`, "ascii"));
    }
    xref.push(
      Buffer.from(
        `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`,
        "ascii",
      ),
    );

    return Buffer.concat([body, ...xref]);
  }

  const escapedText = text.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
  const stream = Buffer.from(`BT\n/F1 12 Tf\n72 720 Td\n(${escapedText}) Tj\nET`, "latin1");

  return assemblePdf([
    Buffer.from("<< /Type /Catalog /Pages 2 0 R >>", "ascii"),
    Buffer.from("<< /Type /Pages /Kids [3 0 R] /Count 1 >>", "ascii"),
    Buffer.from(
      "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
      "ascii",
    ),
    Buffer.concat([
      Buffer.from(`<< /Length ${stream.length} >>\nstream\n`, "ascii"),
      stream,
      Buffer.from("\nendstream", "ascii"),
    ]),
    Buffer.from("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", "ascii"),
  ]);
}


test("operator uploads a contract and reviews the findings", async ({ page }) => {
  await page.goto("/contracts");
  await page.getByLabel("Titulo do contrato").fill("Loja Centro");
  await page.getByLabel("Referencia externa").fill("LOC-001");
  await page.getByLabel("Contrato PDF").setInputFiles({
    name: "third-party-draft.pdf",
    mimeType: "application/pdf",
    buffer: buildPdfWithText("Prazo de vigencia 36 meses"),
  });
  await page.getByRole("button", { name: "Enviar contrato" }).click();

  await expect(page.getByRole("heading", { name: "Findings principais" })).toBeVisible();
  await expect(page.getByText("Prazo de vigencia", { exact: true })).toBeVisible();
  await expect(page.getByText("Critico", { exact: true })).toBeVisible();
});

test("operator sees a readable error for an unreadable pdf upload", async ({ page }) => {
  await page.goto("/contracts");
  await page.getByLabel("Titulo do contrato").fill("Loja Centro");
  await page.getByLabel("Referencia externa").fill("LOC-ERR-001");
  await page.getByLabel("Contrato PDF").setInputFiles("tests/fixtures/unreadable-upload.pdf");
  await page.getByRole("button", { name: "Enviar contrato" }).click();

  await expect(page.locator("p[role='alert']")).toContainText(
    "O arquivo enviado nao e um PDF legivel.",
  );
});
