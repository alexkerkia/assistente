import os
import base64
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import anthropic

app = FastAPI()

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
ZAPI_INSTANCE = os.environ["ZAPI_INSTANCE_ID"]
ZAPI_TOKEN = os.environ["ZAPI_TOKEN"]
ZAPI_CLIENT_TOKEN = os.environ["ZAPI_CLIENT_TOKEN"]
ZAPI_BASE = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}"

CATALOG = [
    {"id":"98499825","nome":"Body Lauren","cor":["azul","soft blue"],"tamanhos":["PP","P","M","G","GG"],"preco":389.90},
    {"id":"98079828","nome":"Calça Cíntia","cor":["off-white","creme"],"tamanhos":["PP","P","M","G","GG"],"preco":319.90},
    {"id":"99499530","nome":"Body Linda","cor":["azul","soft blue"],"tamanhos":["PP","P","M","G","GG"],"preco":359.90},
    {"id":"98439341","nome":"Sutiã Cassia","cor":["azul","soft blue"],"tamanhos":["PP","P","M","G"],"preco":219.90},
    {"id":"99459356","nome":"Calcinha Larissa","cor":["azul","soft blue"],"tamanhos":["PP","P","M","G","GG"],"preco":159.90},
    {"id":"97449245","nome":"Sutiã Alice","cor":["azul","soft blue"],"tamanhos":["PP","P","M","G"],"preco":189.90},
    {"id":"96459384","nome":"Calcinha Jamile","cor":["azul","soft blue"],"tamanhos":["PP","P","M","G","GG"],"preco":169.90},
    {"id":"98127071","nome":"Chamise Ibiza","cor":["azul royal"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90},
    {"id":"99179773","nome":"Camisa Paty","cor":["azul claro"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90},
    {"id":"99049780","nome":"Short Mirela","cor":["azul claro"],"tamanhos":["PP","P","M","G","GG"],"preco":279.90},
    {"id":"98359827","nome":"Saída Mary","cor":["azul claro"],"tamanhos":["PP","P","M","G","GG"],"preco":449.90},
    {"id":"98179832","nome":"Blusa Melina","cor":["azul","listrado"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90},
    {"id":"98079831","nome":"Calça Melina","cor":["azul","listrado"],"tamanhos":["PP","P","M","G","GG"],"preco":329.90},
    {"id":"99449626","nome":"Sutiã Bel","cor":["marrom"],"tamanhos":["PP","P","M","G"],"preco":189.90},
    {"id":"97459047","nome":"Calcinha Musa","cor":["marrom"],"tamanhos":["PP","P","M","G","GG"],"preco":149.90},
    {"id":"97439480","nome":"Top Susane","cor":["marrom"],"tamanhos":["PP","P","M","G"],"preco":229.90},
    {"id":"98462931","nome":"Calcinha Bombom","cor":["marrom"],"tamanhos":["PP","P","M","G","GG"],"preco":159.90},
    {"id":"98412498","nome":"Body New Juju","cor":["marrom"],"tamanhos":["PP","P","M","G","GG"],"preco":359.90},
    {"id":"98492123","nome":"Body Kerk","cor":["marrom"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90},
    {"id":"98399829","nome":"Saia Eva","cor":["off-white"],"tamanhos":["PP","P","M","G","GG"],"preco":289.90},
    {"id":"98279830","nome":"Saída Camila","cor":["azul","listrado","bege"],"tamanhos":["PP","P","M","G","GG"],"preco":389.90},
    {"id":"99499727","nome":"Body Maitê","cor":["azul","listrado","bege"],"tamanhos":["PP","P","M","G","GG"],"preco":339.90},
    {"id":"98444016","nome":"Sutiã Lary","cor":["azul","listrado","bege"],"tamanhos":["PP","P","M","G"],"preco":179.90},
    {"id":"98459469","nome":"Calcinha Isabel","cor":["azul","listrado","bege"],"tamanhos":["PP","P","M","G","GG"],"preco":169.90},
    {"id":"98499353","nome":"Body Helena","cor":["azul","listrado","bege"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90},
    {"id":"90442852","nome":"Sutiã Cindy","cor":["azul","listrado","bege"],"tamanhos":["PP","P","M","G"],"preco":199.90},
    {"id":"98449625","nome":"Calcinha Mariana","cor":["azul","listrado","bege"],"tamanhos":["PP","P","M","G","GG"],"preco":169.90},
    {"id":"98299826","nome":"Body Maria Helena","cor":["azul","listrado","bege"],"tamanhos":["4","6","8","10","12","14"],"preco":169.90},
]

CATALOG_TEXT = "\n".join([
    f"REF {p['id']} | {p['nome']} | cor: {', '.join(p['cor'])} | tamanhos: {', '.join(p['tamanhos'])} | R${p['preco']:.2f}"
    for p in CATALOG
])

SYSTEM_PROMPT = "Você é a KERK Assistente, atendente virtual da KERK Glam Wear (moda praia feminina).\n\nCATÁLOGO:\n" + CATALOG_TEXT + "\n\nQuando receber imagem, identifique a peça e informe: nome, REF, preço e tamanhos. Seja simpática e concisa. Português brasileiro. Sem asteriscos markdown."async def download_image(url: str):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        ct = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
        return base64.b64encode(r.content).decode(), ct


async def ask_claude(text: str, image_url: str = None) -> str:
    content = []
    if image_url:
        try:
            b64, mt = await download_image(image_url)
            content.append({"type": "image", "source": {"type": "base64", "media_type": mt, "data": b64}})
            print(f"Imagem ok: {mt}")
        except Exception as e:
            print(f"Erro imagem: {e}")
    content.append({"type": "text", "text": text or "Que peca e essa?"})
    print("Chamando Claude...")
    r = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )
    reply = r.content[0].text
    print(f"Claude: {reply[:80]}")
    return reply


async def send_whatsapp(phone: str, message: str):
    url = f"{ZAPI_BASE}/send-text"
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json={"phone": phone, "message": message}, headers=headers)
        print(f"ZAPI: {r.status_code} {r.text}")
        r.raise_for_status()


@app.get("/")
def health():
    return {"status": "KERK Assistente online"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        phone = body.get("phone", "")
        print(f"Webhook: type={body.get('type')} phone={phone} fromMe={body.get('fromMe')}")

        if not phone or body.get("fromMe", False):
            return JSONResponse({"ok": True})

        msg = body.get("message", {})
        text = ""
        image_url = None

        if "text" in msg:
            t = msg["text"]
            text = t.get("message", "") if isinstance(t, dict) else str(t)
        elif "image" in msg:
            img = msg["image"]
            image_url = img.get("imageUrl") or img.get("url", "")
            text = img.get("caption", "") or "Que peca e essa?"

        print(f"text={text!r} image_url={image_url!r}")

        if not text and not image_url:
            return JSONResponse({"ok": True})

        reply = await ask_claude(text, image_url)
        await send_whatsapp(phone, reply)
        print("Enviado!")
        return JSONResponse({"ok": True})

    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
