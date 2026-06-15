import os
import base64
import httpx
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import anthropic

app = FastAPI()

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
ZAPI_INSTANCE  = os.environ["ZAPI_INSTANCE_ID"]
ZAPI_TOKEN     = os.environ["ZAPI_TOKEN"]
ZAPI_CLIENT_TOKEN = os.environ["ZAPI_CLIENT_TOKEN"]
ZAPI_BASE      = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}"

CATALOG = [
    {"id":"98499825","nome":"Body Lauren","tipo":"body","cor":["azul","soft blue"],"detalhes":["franzido","halter neck","detalhe dourado"],"tamanhos":["PP","P","M","G","GG"],"preco":389.90,"colecao":"Navy"},
    {"id":"98079828","nome":"Calça Cíntia","tipo":"calça","cor":["off-white","creme"],"detalhes":["fluida","cós largo franzido","wide leg"],"tamanhos":["PP","P","M","G","GG"],"preco":319.90,"colecao":"Navy"},
    {"id":"99499530","nome":"Body Linda","tipo":"body","cor":["azul","soft blue"],"detalhes":["alças largas","decote quadrado","liso"],"tamanhos":["PP","P","M","G","GG"],"preco":359.90,"colecao":"Navy"},
    {"id":"98439341","nome":"Sutiã Cassia","tipo":"sutiã","cor":["azul","soft blue"],"detalhes":["franzido","bandeau","tomara que caia"],"tamanhos":["PP","P","M","G"],"preco":219.90,"colecao":"Navy"},
    {"id":"99459356","nome":"Calcinha Larissa","tipo":"calcinha","cor":["azul","soft blue"],"detalhes":["liso","básica"],"tamanhos":["PP","P","M","G","GG"],"preco":159.90,"colecao":"Navy"},
    {"id":"97449245","nome":"Sutiã Alice","tipo":"sutiã","cor":["azul","soft blue"],"detalhes":["triangulo","amarração","dourado"],"tamanhos":["PP","P","M","G"],"preco":189.90,"colecao":"Navy"},
    {"id":"96459384","nome":"Calcinha Jamile","tipo":"calcinha","cor":["azul","soft blue"],"detalhes":["amarração lateral","dourado"],"tamanhos":["PP","P","M","G","GG"],"preco":169.90,"colecao":"Navy"},
    {"id":"98127071","nome":"Chamise Ibiza","tipo":"camisa","cor":["azul royal","azul escuro"],"detalhes":["abertura nas costas","manga longa","botões"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90,"colecao":"Navy"},
    {"id":"99179773","nome":"Camisa Paty","tipo":"camisa","cor":["azul claro"],"detalhes":["bordado dourado","palmeiras","manga curta"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90,"colecao":"Navy Resort"},
    {"id":"99049780","nome":"Short Mirela","tipo":"short","cor":["azul claro"],"detalhes":["bordado dourado","palmeiras"],"tamanhos":["PP","P","M","G","GG"],"preco":279.90,"colecao":"Navy Resort"},
    {"id":"98359827","nome":"Saída Mary","tipo":"saída de praia","cor":["azul claro"],"detalhes":["bordado dourado","palmeiras","longo"],"tamanhos":["PP","P","M","G","GG"],"preco":449.90,"colecao":"Navy Resort"},
    {"id":"98179832","nome":"Blusa Melina","tipo":"blusa","cor":["azul","listrado","branco"],"detalhes":["listrado","manga longa","oversized"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90,"colecao":"Navy Resort"},
    {"id":"98079831","nome":"Calça Melina","tipo":"calça","cor":["azul","listrado","branco"],"detalhes":["listrado","pantalona"],"tamanhos":["PP","P","M","G","GG"],"preco":329.90,"colecao":"Navy Resort"},
    {"id":"99449626","nome":"Sutiã Bel","tipo":"sutiã","cor":["marrom","chocolate"],"detalhes":["triangulo","pérola"],"tamanhos":["PP","P","M","G"],"preco":189.90,"colecao":"Navy"},
    {"id":"97459047","nome":"Calcinha Musa","tipo":"calcinha","cor":["marrom","chocolate"],"detalhes":["liso"],"tamanhos":["PP","P","M","G","GG"],"preco":149.90,"colecao":"Navy"},
    {"id":"97439480","nome":"Top Susane","tipo":"top","cor":["marrom","chocolate"],"detalhes":["bandeau","dourado"],"tamanhos":["PP","P","M","G"],"preco":229.90,"colecao":"Navy"},
    {"id":"98462931","nome":"Calcinha Bombom","tipo":"calcinha","cor":["marrom","chocolate"],"detalhes":["franzida"],"tamanhos":["PP","P","M","G","GG"],"preco":159.90,"colecao":"Navy"},
    {"id":"98412498","nome":"Body New Juju","tipo":"body","cor":["marrom","chocolate"],"detalhes":["decote V","drapeado","nó frontal"],"tamanhos":["PP","P","M","G","GG"],"preco":359.90,"colecao":"Navy"},
    {"id":"98492123","nome":"Body Kerk","tipo":"body","cor":["marrom","chocolate"],"detalhes":["decote nadador","costas abertas"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90,"colecao":"Navy Essentials"},
    {"id":"98399829","nome":"Saia Eva","tipo":"saia","cor":["off-white","creme"],"detalhes":["drapeada","fenda"],"tamanhos":["PP","P","M","G","GG"],"preco":289.90,"colecao":"Navy"},
    {"id":"98279830","nome":"Saída Camila","tipo":"saída de praia","cor":["azul","listrado","bege"],"detalhes":["listrado","vivo marrom","longo"],"tamanhos":["PP","P","M","G","GG"],"preco":389.90,"colecao":"Navy Mood"},
    {"id":"99499727","nome":"Body Maitê","tipo":"body","cor":["azul","listrado","bege"],"detalhes":["listrado","alças finas","vivo marrom"],"tamanhos":["PP","P","M","G","GG"],"preco":339.90,"colecao":"Navy"},
    {"id":"98444016","nome":"Sutiã Lary","tipo":"sutiã","cor":["azul","listrado","bege"],"detalhes":["listrado","triangulo"],"tamanhos":["PP","P","M","G"],"preco":179.90,"colecao":"Navy"},
    {"id":"98459469","nome":"Calcinha Isabel","tipo":"calcinha","cor":["azul","listrado","bege"],"detalhes":["listrado","amarração"],"tamanhos":["PP","P","M","G","GG"],"preco":169.90,"colecao":"Navy"},
    {"id":"98499353","nome":"Body Helena","tipo":"body","cor":["azul","listrado","bege"],"detalhes":["listrado","halter neck","franzido lateral"],"tamanhos":["PP","P","M","G","GG"],"preco":349.90,"colecao":"Navy"},
    {"id":"90442852","nome":"Sutiã Cindy","tipo":"sutiã","cor":["azul","listrado","bege"],"detalhes":["listrado","bojo","vivo marrom"],"tamanhos":["PP","P","M","G"],"preco":199.90,"colecao":"Navy Essentials"},
    {"id":"98449625","nome":"Calcinha Mariana","tipo":"calcinha","cor":["azul","listrado","bege"],"detalhes":["listrado","cintura alta"],"tamanhos":["PP","P","M","G","GG"],"preco":169.90,"colecao":"Navy Essentials"},
    {"id":"98299826","nome":"Body Maria Helena","tipo":"body","cor":["azul","listrado","bege"],"detalhes":["kids","abertura nas costas"],"tamanhos":["4","6","8","10","12","14"],"preco":169.90,"colecao":"Navy Kids"},
]

CATALOG_TEXT = "\n".join([
    f"REF {p['id']} | {p['nome']} | {p['tipo']} | cor: {', '.join(p['cor'])} | "
    f"detalhes: {', '.join(p['detalhes'])} | tamanhos: {', '.join(p['tamanhos'])} | "
    f"R${p['preco']:.2f} | {p['colecao']}"
    for p in CATALOG
])

SYSTEM_PROMPT = f"""Você é a KERK Assistente, atendente virtual da marca KERK Glam Wear (moda praia feminina).

CATÁLOGO COMPLETO KERK NAVY:
{CATALOG_TEXT}

REGRAS:
- Quando receber uma imagem, analise visualmente e identifique qual(is) peça(s) do catálogo aparecem.
- Responda sempre com: nome da peça, REF, preço, tamanhos disponíveis e coleção.
- Se a foto mostrar mais de uma peça, informe todas.
- Se não conseguir identificar com certeza, aponte a mais próxima e pergunte se é essa.
- Nunca invente produtos fora do catálogo acima.
- Seja simpática, elegante e concisa. Linguagem de WhatsApp.
- Sempre em português brasileiro.
- Tom: consultora de moda pessoal, confiante e acolhedora.
- Nunca use markdown com asteriscos — o WhatsApp usa *negrito* nativamente."""


async def download_image(url: str) -> tuple[str, str]:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        ct = r.headers.get("content-type", "image/jpeg")
        media_type = ct.split(";")[0].strip()
        b64 = base64.b64encode(r.content).decode()
        return b64, media_type


async def ask_claude(text: str, image_url: str = None) -> str:
    content = []
    if image_url:
        try:
            b64, media_type = await download_image(image_url)
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": me
