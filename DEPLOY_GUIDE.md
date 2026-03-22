# 🚀 Guia de Deploy - LegalBoard

## PASSO 1: Backend no Railway

### 1.1 Acesse o Railway
- Vá para: https://railway.app
- Clique em "Login" → "Login with GitHub"

### 1.2 Crie um novo projeto
- Clique em "New Project"
- Selecione "Deploy from GitHub repo"
- Escolha: `cauedev30/projeto-yuann`

### 1.3 Configure o serviço
- Clique no serviço criado
- Vá em "Settings"
- Em "Root Directory" coloque: `backend`

### 1.4 Adicione as variáveis de ambiente
Vá em "Variables" e adicione:

| Nome | Valor |
|------|-------|
| `OPENAI_API_KEY` | Sua chave da OpenAI (gere uma nova em platform.openai.com) |
| `JWT_SECRET` | `qfoviL+RZCwVt9poKFaFrgV9fQX/0Fmxr0VDpsEZJrQ=` |

### 1.5 Pegue a URL do backend
- Vá em "Settings" → "Networking" → "Generate Domain"
- Copie a URL (ex: `https://projeto-yuann-production.up.railway.app`)

---

## PASSO 2: Frontend no Vercel

### 2.1 Na tela de configuração do Vercel
- **Root Directory**: Clique em "Edit" e digite `web`
- O Framework vai mudar para "Next.js" automaticamente

### 2.2 Adicione a variável de ambiente
Clique em "Environment Variables" e adicione:

| Nome | Valor |
|------|-------|
| `NEXT_PUBLIC_API_URL` | A URL do Railway (do passo 1.5) |

### 2.3 Deploy
- Clique no botão "Deploy"
- Aguarde finalizar

---

## ✅ Pronto!

Seu app estará disponível em:
- Frontend: `https://projeto-yuann.vercel.app`
- Backend: `https://projeto-yuann-production.up.railway.app`

---

## ⚠️ IMPORTANTE

Sua chave OPENAI_API_KEY antiga está exposta no repositório público.
Vá em https://platform.openai.com/api-keys e:
1. Revogue a chave antiga
2. Crie uma nova
3. Use a nova no Railway
