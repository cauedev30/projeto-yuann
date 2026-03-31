# Guia de Deploy - LegalBoard

Este repositório está preparado para:

- `backend/` no Railway
- `web/` no Vercel

O backend agora aceita `DATABASE_URL`, `UPLOAD_DIR` e `CORS_ORIGINS` por variável de ambiente. Para produção, use `Postgres` e um volume no Railway para os uploads.

## Arquitetura recomendada

- Backend: Railway
- Banco: Postgres no Railway
- Arquivos enviados: volume do Railway montado em `/data`
- Frontend: Vercel

## Passo 1: Backend no Railway

### 1.1 Criar o serviço

1. Crie um novo projeto no Railway a partir do repositório `cauedev30/projeto-yuann`.
2. No serviço do backend, configure `Root Directory = backend`.

### 1.2 Adicionar Postgres

1. No mesmo projeto Railway, adicione um serviço `Postgres`.
2. Copie a variável `DATABASE_URL` gerada pelo Railway.

### 1.3 Adicionar um volume para uploads

1. No serviço do backend, adicione um `Volume`.
2. Monte o volume em `/data`.
3. Use `UPLOAD_DIR=/data/uploads`.

Sem volume, os arquivos enviados podem ser perdidos após restart ou novo deploy.

### 1.4 Variáveis de ambiente do backend

Configure estas variáveis no serviço `backend`:

| Nome | Valor |
| --- | --- |
| `DATABASE_URL` | valor do Postgres gerado pelo Railway |
| `UPLOAD_DIR` | `/data/uploads` |
| `CORS_ORIGINS` | URL final do frontend no Vercel |
| `JWT_SECRET` | segredo forte gerado por você |
| `JWT_EXPIRATION_MINUTES` | `480` |
| `OPENAI_API_KEY` | opcional, se quiser usar OpenAI |
| `GOOGLE_API_KEY` | opcional, se quiser usar Gemini |

Observações:

- Defina apenas uma chave LLM por vez se quiser um comportamento previsível.
- Se nenhuma chave for configurada, o runtime sobe, mas recursos de IA podem cair para comportamento limitado.
- `SMTP_ENABLED`, `MAILPIT_SMTP_HOST` e `MAILPIT_SMTP_PORT` são opcionais para produção atual.

### 1.5 Gerar domínio público do backend

1. No Railway, abra o serviço do backend.
2. Vá em `Settings` -> `Networking`.
3. Gere um domínio público.
4. Guarde a URL, por exemplo `https://legalboard-api.up.railway.app`.

### 1.6 Verificar o backend

Depois do deploy, valide:

```txt
GET https://<seu-backend>/health
```

Resposta esperada:

```json
{"status":"ok"}
```

Se o banco do Railway ja existia antes das colunas mais recentes do projeto, rode as migrations do backend antes de validar as rotas:

```txt
cd backend && alembic upgrade head
```

## Passo 2: Frontend no Vercel

### 2.1 Criar o projeto

1. Importe o mesmo repositório no Vercel.
2. Configure `Root Directory = web`.
3. O framework deve ser detectado como `Next.js`.

### 2.2 Variável de ambiente do frontend

Configure no Vercel:

| Nome | Valor |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | URL pública do backend no Railway |

Exemplo:

```txt
NEXT_PUBLIC_API_URL=https://legalboard-api.up.railway.app
```

### 2.3 Fazer o deploy

Execute o deploy no Vercel e guarde a URL final do frontend.

## Passo 3: Fechar o CORS

Depois de ter a URL final do Vercel:

1. Volte ao Railway.
2. Atualize `CORS_ORIGINS` para a URL exata do frontend.

Exemplo:

```txt
CORS_ORIGINS=https://projeto-yuann.vercel.app
```

Se você usar preview deployments do Vercel e quiser permitir mais de um domínio, use lista separada por vírgula:

```txt
CORS_ORIGINS=https://projeto-yuann.vercel.app,https://projeto-yuann-git-main-seuusuario.vercel.app
```

## Checklist final

- Railway com `Root Directory = backend`
- Vercel com `Root Directory = web`
- `DATABASE_URL` apontando para Postgres
- `UPLOAD_DIR=/data/uploads`
- volume montado em `/data`
- `CORS_ORIGINS` com a URL do Vercel
- `NEXT_PUBLIC_API_URL` com a URL do Railway
- `JWT_SECRET` forte e novo
- endpoint `/health` respondendo `200`

## Se algo falhar

Os erros mais prováveis são:

- `CORS` bloqueando chamadas do Vercel para o Railway
- `DATABASE_URL` ausente ou inválido
- falta de volume para `UPLOAD_DIR`
- `NEXT_PUBLIC_API_URL` apontando para a URL errada
- segredo JWT ausente
