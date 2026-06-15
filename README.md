# KERK Assistente — Backend

## Deploy no Railway

1. Acesse railway.app e crie conta
2. Clique em "New Project" → "Deploy from GitHub repo"
3. Faça upload desta pasta ou conecte ao GitHub
4. Configure as variáveis de ambiente (Settings > Variables):
   - ANTHROPIC_API_KEY
   - ZAPI_INSTANCE_ID
   - ZAPI_TOKEN
   - ZAPI_CLIENT_TOKEN
5. O Railway faz o deploy automaticamente
6. Copie a URL gerada (ex: kerk-backend.up.railway.app)

## Configurar Webhook no Z-API

Após o deploy, vá no painel Z-API:
- Webhook de recebimento: https://SUA_URL.railway.app/webhook
- Marcar: Mensagens recebidas, Imagens

## Testar localmente

```bash
pip install -r requirements.txt
cp .env.example .env
# preencher .env com suas chaves
uvicorn main:app --reload
```
