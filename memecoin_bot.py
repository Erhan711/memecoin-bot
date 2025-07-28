import telebot
import requests
import time

BOT_TOKEN = "8210998239:AAFpRL8dtiVwsQF4HZgMrYiU4RLfqBVAQ5s"
bot = telebot.TeleBot(BOT_TOKEN)

def hesapla_ai_skor(hacim, likidite, honeypot):
    skor = 50
    if hacim > 50000:
        skor += 20
    if likidite > 10000:
        skor += 20
    if honeypot:
        skor -= 60
    return max(0, min(100, skor))

def honeypot_kontrolu(address, chain):
    try:
        zincir = {"bsc": "bsc", "eth": "eth", "base": "base"}.get(chain, "eth")
        url = f"https://api.honeypot.is/v1/IsHoneypot?address={address}&chain={zincir}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data.get("honeypotResult", {}).get("isHoneypot", False)
    except:
        return False

def yeni_tokenler():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    response = requests.get(url)
    if response.status_code != 200:
        return ["API hatası: DexScreener erişilemedi."]
    data = response.json()
    sonuc = []
    for token in data["pairs"][:5]:
        isim = token.get("baseToken", {}).get("name", "N/A")
        sembol = token.get("baseToken", {}).get("symbol", "")
        zincir = token.get("chainId", "unknown")
        hacim = token.get("volume", {}).get("h24", 0)
        likidite = token.get("liquidity", {}).get("usd", 0)
        adres = token.get("baseToken", {}).get("address", "")
        honeypot = honeypot_kontrolu(adres, zincir)
        skor = hesapla_ai_skor(hacim, likidite, honeypot)

        mesaj = f"🚀 <b>{isim} ({sembol})</b>\n"
        mesaj += f"🔗 Zincir: <code>{zincir}</code>\n"
        mesaj += f"💰 Hacim (24h): ${int(hacim):,}\n"
        mesaj += f"💧 Likidite: ${int(likidite):,}\n"
        mesaj += f"⚠️ Honeypot: {'Evet' if honeypot else 'Hayır'}\n"
        mesaj += f"🤖 AI Token Skoru: <b>{skor}/100</b>\n"
        mesaj += f"🔎 Dex: {token.get('url', '')}\n"
        mesaj += "──────────────\n"
        sonuc.append(mesaj)
        time.sleep(1.2)
    return sonuc

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🆕 Yeni Tokenler", "📈 Hacim Artışı")
    markup.row("🧪 Testnet Tokenler", "🤖 AI Token Skoru")
    bot.send_message(message.chat.id, "👋 Hoş geldin! Aşağıdan bir seçenek seç:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🆕 Yeni Tokenler")
def yeni_token_cevapla(message):
    bot.send_message(message.chat.id, "🔍 Canlı olarak yeni çıkan tokenler aranıyor...")
    try:
        tokenler = yeni_tokenler()
        for tkn in tokenler:
            bot.send_message(message.chat.id, tkn, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Hata oluştu: {str(e)}")

@bot.message_handler(func=lambda message: True)
def genel_cevap(message):
    bot.send_message(message.chat.id, "⚠️ Bu özellik henüz aktif değil. Yakında eklenecek!")

bot.polling(none_stop=True)
