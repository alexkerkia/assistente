import os, base64, httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import anthropic

app = FastAPI()
ac = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
ZB = f"https://api.z-api.io/instances/{os.environ['ZAPI_INSTANCE_ID']}/token/{os.environ['ZAPI_TOKEN']}"
CT = os.environ["ZAPI_CLIENT_TOKEN"]

SP = """Voce e a KERK Assistente, atendente virtual da KERK Glam Wear.
Catalogo: Body Lauren R$389.90 REF 98499825 | Calca Cintia R$319.90 REF 98079828 | Body Linda R$359.90 REF 99499530 | Sutia Cassia R$219.90 REF 98439341 | Calcinha Larissa R$159.90 REF 99459356 | Sutia Alice R$189.90 REF 97449245 | Calcinha Jamile R$169.90 REF 96459384 | Chamise Ibiza R$349.90 REF 98127071 | Camisa Paty R$349.90 REF 99179773 | Short Mirela R$279.90 REF 99049780 | Saida Mary R$449.90 REF 98359827 | Blusa Melina R$349.90 REF 98179832 | Calca Melina R$329.90 REF 98079831 | Sutia Bel R$189.90 REF 99449626 | Calcinha Musa R$149.90 REF 97459047 | Top Susane R$229.90 REF 97439480 | Calcinha Bombom R$159.90 REF 98462931 | Body New Juju R$359.90 REF 98412498 | Body Kerk R$349.90 REF 98492123 | Saia Eva R$289.90 REF 98399829 | Saida Camila R$389.90 REF 98279830 | Body Maite R$339.90 REF 99499727 | Sutia Lary R$179.90 REF 98444016 | Calcinha Isabel R$169.90 REF 98459469 | Body Helena R$349.90 REF 98499353 | Sutia Cindy R$199.90 REF 90442852 | Calcinha Mariana R$169.90 REF 98449625 | Body Maria Helena R$169.90 REF 98299826
Quando receber imagem identifique a peca e informe nome REF preco e tamanhos. Seja simpatica e concisa em portugues brasileiro."""


async def get_img(url):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(url)
        r.raise_for_status()
        mt = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
        return base64.b64encode(r.content).decode(), mt


async def claude(text, img_url=None):
    content = []
    if img_url:
        try:
            b64, mt = await get_img(img_url)
            content.append({"type": "image", "source": {"type": "base64", "media_type": mt, "data": b64}})
            print("Imagem ok")
        except Exception as e:
            print(f"Erro imagem: {e}")
    content.append({"type": "text", "text": text or "Que peca e essa?"})
    print("Chamando Claude...")
    r = ac.messages.create(model="claude-sonnet-4-6", max_tokens=800, system=SP, messages=[{"role": "user", "content": content}])
    reply = r.content[0].text
    print(f"Resposta: {reply[:80]}")
    return reply


async def zapi(phone, msg):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{ZB}/send-text", json={"phone": phone, "message": msg}, headers={"Client-Token": CT})
        print(f"ZAPI {r.status_code}: {r.text[:80]}")
        r.raise_for_status()


@app.get("/")
def health():
    return {"status": "KERK Assistente online"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        phone = body.get("phone", "")
        print(f"Webhook phone={phone} fromMe={body.get('fromMe')} type={body.get('type')}")

        if not phone or body.get("fromMe"):
            return JSONResponse({"ok": True})

        text = ""
        img_url = None

        if "image" in body:
            img = body["image"]
            img_url = img.get("imageUrl") or img.get("url", "")
            text = img.get("caption", "") or "Que peca e essa?"
        elif "text" in body:
            t = body["text"]
            text = t.get("message", "") if isinstance(t, dict) else str(t)
        else:
            msg = body.get("message", {})
            if "image" in msg:
                img = msg["image"]
                img_url = img.get("imageUrl") or img.get("url", "")
                text = img.get("caption", "") or "Que peca e essa?"
            elif "text" in msg:
                t = msg["text"]
                text = t.get("message", "") if isinstance(t, dict) else str(t)

        print(f"text={text!r} img={img_url!r}")

        if not text and not img_url:
            return JSONResponse({"ok": True})

        reply = await claude(text, img_url)
        await zapi(phone, reply)
        print("Enviado!")
        return JSONResponse({"ok": True})

    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
