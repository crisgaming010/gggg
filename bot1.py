import logging, os, zipfile, tempfile, base64, json, time, datetime, re, struct, math, hashlib, sys, requests, threading, aiohttp, gzip, asyncio, random, sqlite3
from io import BytesIO
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler)
from telegram.request import HTTPXRequest
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
from Crypto.Hash import SHA1
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
try:
    import brotli
except ImportError:
    brotli = None

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN = "8754288681:AAEPM-jntmZafaxqj7CgbvHQBlT0kt6kWxw"
ADMIN_ID = [7634875658]
OWNER_USERNAME = "@Maarkryan"
COIN_FILE = "coins.json"
USERS_FILE = "users.txt"
USERS_LOG = "users_log.json"
STATS_FILE = "user_stats.json"
LANG_FILE = "user_langs.json"

CPM1_API_KEY = "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"
CPM2_API_KEY = "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
CPM1_DATABASE_URL = "https://carparkingmultiplayer-dc1d2.firebaseio.com"
CPM1_API_BASE = "https://us-central1-carparkingmultiplayer-dc1d2.cloudfunctions.net"
CPM2_API_BASE = "https://europe-west1-cpm-2-7cea1.cloudfunctions.net"
CPM1_FALLBACK_BASES = (
    "https://europe-west1-cp-multiplayer.cloudfunctions.net",
    "https://us-central1-cp-multiplayer.cloudfunctions.net",
)
CPM1_CARS_FUNCTION = "GetAllCars2"
CPM2_CARS_FUNCTION_CANDIDATES = (
    "GetAllCars24_1", "GetAllCars23_1", "GetAllCars22_1",
    "GetAllCars21_1", "GetAllCars20_2",
)
CPM2_SAVE_CAR_FUNCTION = "SaveCar22_1"

CF_BASE = 'https://europe-west1-cpm-2-7cea1.cloudfunctions.net'
KEY_ADD = '12345678'
IV_ADD = '01234567'

COST_CPM_PASS = 10
COST_CONVERSION = 30
COST_VINYL_API = 65
COST_UNLOCK = 80
COST_FARM = 50

USD_TO_PHP = 62.58
ITEMS_PER_PAGE = 8

# Ranks
RANKS = [
    (501, "EFSANE", "🔴", 999999),
    (101, "ELIT", "🟠", 50),
    (51, "USTA", "🟣", 30),
    (11, "DENEYIMLI", "🔵", 20),
    (0, "CAYLAK", "🟢", 10),
]

def get_rank(total):
    for min_ops, name, emoji, daily in RANKS:
        if total >= min_ops: return name, emoji, daily
    return "CAYLAK", "🟢", 10

# ============================================================
# STATES
# ============================================================
WAIT_MENU = 0
WAIT_FILE = 1
WAIT_EMAIL = 2
WAIT_PASSWORD = 3
WAIT_CPM1_FILE = 4
WAIT_CPM1_EMAIL = 5
WAIT_CPM1_PASSWORD = 6
WAIT_CPM2_FILE = 7
WAIT_CPM2_EMAIL = 8
WAIT_CPM2_PASSWORD = 9
WAIT_LOGIN_EMAIL = 10
WAIT_LOGIN_PASSWORD = 11
WAIT_NEW_EMAIL = 12
WAIT_NEW_PASSWORD = 13
WAIT_ZIP = 14
WAIT_CPM2A_FILE = 15
WAIT_CPM2A_EMAIL = 16
WAIT_CPM2A_PASSWORD = 17
WAIT_CPM2B_FILE = 18
WAIT_CPM2B_EMAIL = 19
WAIT_CPM2B_PASSWORD = 20
WAIT_API_CPM1_CREDS = 21
WAIT_API_CPM2_CREDS = 22
WAIT_FARM_EMAIL = 23
WAIT_FARM_PASSWORD = 24

sessions = defaultdict(dict)
saved_cpm2_accounts = {}
_cars_function_name = None

# ============================================================
# LANGUAGE SYSTEM
# ============================================================
TRANSLATIONS = {
    "en": {
        "lang_name": "🇬🇧 English",
        "select_lang": "🌐 Select Language",
        "welcome": "🎮 <b>MARK CPM TOOL</b> 🎮\n<i>Premium Suite v2.0</i>",
        "account": "Account",
        "user_id": "User ID",
        "wallet": "WALLET",
        "coins": "Coins",
        "status": "Status",
        "unlimited": "👑 Unlimited",
        "standard": "🪙 Standard",
        "subscription": "SUBSCRIPTION",
        "plan": "Plan",
        "expires": "Expires",
        "lifetime": "👑 Lifetime",
        "never": "Never expires",
        "active": "✅ Active",
        "none": "❌ None",
        "statistics": "STATISTICS",
        "operations": "Operations",
        "member_since": "Member Since",
        "select_feature": "⚡ Select a feature from the menu below",
        "account_tools": "ACCOUNT TOOLS",
        "cpm1_pass": "🔐 CPM1 Pass",
        "cpm2_pass": "🔐 CPM2 Pass",
        "conversion": "CONVERSION",
        "cpm1_to_cpm2": "📀 CPM1 → CPM2 (Manual)",
        "cpm2_to_cpm2": "📀 CPM2 → CPM2 (Manual)",
        "premium": "PREMIUM FEATURES",
        "api_vinyl": "🎨 API Vinyl Transfer (1-Click) ⚡",
        "garage": "GARAGE MODS",
        "unlock_all": "🔥 Unlock All",
        "body_mods": "🚗 Full Body Mods",
        "upload_zip": "📦 Upload ES3 Folder (ZIP)",
        "info": "INFO",
        "pricing": "💎 Pricing & Plans",
        "contact": "📞 Contact Admin",
        "language": "🌐 Language",
        "coin_farm": "🚗 Coin Farm",
        "rank": "🏆 Rank",
        "full_unlock": "🔥 FULL UNLOCK",
        "individual": "🛠️ INDIVIDUAL PARTS",
        "save_file": "📦 SAVE FILE (ZIP)",
        "main_menu": "🔙 Main Menu",
        "exit_garage": "❌ EXIT GARAGE",
        "air_sus": "🚗 Air Suspension Only",
        "police": "🚓 Police Mods Only",
        "bodykits": "🎨 Bodykits Only",
        "mileage": "📉 Mileage Reset",
        "front_bumper": "🔧 Remove Front Bumper",
        "rear_bumper": "🔧 Remove Rear Bumper",
        "back_garage": "🔙 Back to Garage",
        "back": "🔙 Back",
        "cancel": "❌ Cancel",
        "send_creds": "Send your credentials as <code>email:password</code>",
        "connecting": "⏳ Connecting...",
        "select_src": "👇 Select SOURCE car",
        "select_tgt": "👇 Select TARGET car",
        "connected": "Connected! Found",
        "cars": "cars",
        "transfer_complete": "Transfer Completed!",
        "transfer_failed": "Transfer Failed",
        "source": "Source",
        "target": "Target",
        "need_coins": "❌ Need {amount} coins. You have {have}.",
        "insufficient": "❌ Insufficient coins",
        "applying": "Applying {mod}...",
        "done": "Done",
        "total": "Total",
        "processed": "Processed",
        "modified": "Modified",
        "failed": "Failed",
        "upload_es3": "📦 Send your ES3 folder as a .zip file",
        "sending_creds": "📧 Send your CPM1 email",
        "farm_prompt": "🚗 <b>Coin Farm</b>\n\n📧 Send your CPM2 email:",
        "farm_pass": "🔑 Send your CPM2 password:",
        "farm_running": "⏳ Farm starting...",
        "farm_done": "✅ FARM COMPLETE!",
        "farm_start": "Starting",
        "farm_earned": "Earned",
        "farm_final": "Final",
        "farm_success": "Success",
        "rank_title": "🏆 RANK SYSTEM",
        "your_rank": "Your Rank",
        "rank_list": "Ranks:\n🟢 CAYLAK: 10 ops/day\n🔵 DENEYIMLI: 20 ops/day\n🟣 USTA: 30 ops/day\n🟠 ELIT: 50 ops/day\n🔴 EFSANE: Unlimited",
        "lang_saved": "✅ Language saved!",
    },
    "tl": {
        "lang_name": "🇵🇭 Tagalog",
        "select_lang": "🌐 Pumili ng Wika",
        "welcome": "🎮 <b>MARK CPM TOOL</b> 🎮\n<i>Premium Suite v2.0</i>",
        "account": "Account",
        "user_id": "User ID",
        "wallet": "PITAKA",
        "coins": "Coins",
        "status": "Status",
        "unlimited": "👑 Walang Hanggan",
        "standard": "🪙 Karaniwan",
        "subscription": "SUBSCRIPTION",
        "plan": "Plano",
        "expires": "Mag-e-expire",
        "lifetime": "👑 Habang Buhay",
        "never": "Hindi mag-e-expire",
        "active": "✅ Aktibo",
        "none": "❌ Wala",
        "statistics": "ESTADISTIKA",
        "operations": "Operasyon",
        "member_since": "Miyembro Mula",
        "select_feature": "⚡ Pumili ng feature sa menu sa ibaba",
        "account_tools": "MGA TOOLS",
        "cpm1_pass": "🔐 CPM1 Pass",
        "cpm2_pass": "🔐 CPM2 Pass",
        "conversion": "KONBERSYON",
        "cpm1_to_cpm2": "📀 CPM1 → CPM2 (Manual)",
        "cpm2_to_cpm2": "📀 CPM2 → CPM2 (Manual)",
        "premium": "PREMIUM FEATURES",
        "api_vinyl": "🎨 API Vinyl Transfer (1-Click) ⚡",
        "garage": "GARAGE MODS",
        "unlock_all": "🔥 I-unlock Lahat",
        "body_mods": "🚗 Buong Body Mods",
        "upload_zip": "📦 I-upload ang ES3 Folder (ZIP)",
        "info": "IMPORMASYON",
        "pricing": "💎 Presyo at Plano",
        "contact": "📞 Kontakin ang Admin",
        "language": "🌐 Wika",
        "coin_farm": "🚗 Coin Farm",
        "rank": "🏆 Ranggo",
        "full_unlock": "🔥 FULL UNLOCK",
        "individual": "🛠️ INDIBIDWAL NA PARTS",
        "save_file": "📦 I-SAVE ANG FILE (ZIP)",
        "main_menu": "🔙 Pangunahing Menu",
        "exit_garage": "❌ Lumabas sa Garage",
        "air_sus": "🚗 Air Suspension Lang",
        "police": "🚓 Police Mods Lang",
        "bodykits": "🎨 Bodykits Lang",
        "mileage": "📉 Mileage Reset",
        "front_bumper": "🔧 Alisin ang Front Bumper",
        "rear_bumper": "🔧 Alisin ang Rear Bumper",
        "back_garage": "🔙 Bumalik sa Garage",
        "back": "🔙 Bumalik",
        "cancel": "❌ Kanselahin",
        "send_creds": "Ipadala ang credentials as <code>email:password</code>",
        "connecting": "⏳ Kumokonekta...",
        "select_src": "👇 Pumili ng SOURCE na sasakyan",
        "select_tgt": "👇 Pumili ng TARGET na sasakyan",
        "connected": "Konektado! Nahanap",
        "cars": "mga sasakyan",
        "transfer_complete": "Tapos na ang Transfer!",
        "transfer_failed": "Nabigo ang Transfer",
        "source": "Pinagmulan",
        "target": "Pupuntahan",
        "need_coins": "❌ Kailangan ng {amount} coins. Mayroon ka {have}.",
        "insufficient": "❌ Kulang ang coins",
        "applying": "Ina-apply ang {mod}...",
        "done": "Tapos",
        "total": "Kabuuan",
        "processed": "Naproseso",
        "modified": "Nabago",
        "failed": "Nabigo",
        "upload_es3": "📦 Ipadala ang ES3 folder as .zip file",
        "sending_creds": "📧 Ipadala ang CPM1 email",
        "farm_prompt": "🚗 <b>Coin Farm</b>\n\n📧 Ipadala ang CPM2 email:",
        "farm_pass": "🔑 Ipadala ang CPM2 password:",
        "farm_running": "⏳ Nagsisimula ang farm...",
        "farm_done": "✅ TAPOS NA ANG FARM!",
        "farm_start": "Simula",
        "farm_earned": "Kinita",
        "farm_final": "Panghuli",
        "farm_success": "Tagumpay",
        "rank_title": "🏆 RANGGO SYSTEM",
        "your_rank": "Iyong Ranggo",
        "rank_list": "Mga Ranggo:\n🟢 CAYLAK: 10 ops/araw\n🔵 DENEYIMLI: 20 ops/araw\n🟣 USTA: 30 ops/araw\n🟠 ELIT: 50 ops/araw\n🔴 EFSANE: Walang Hanggan",
        "lang_saved": "✅ Nai-save ang wika!",
    },
    "es": {
        "lang_name": "🇪🇸 Español",
        "select_lang": "🌐 Seleccionar Idioma",
        "welcome": "🎮 <b>MARK CPM TOOL</b> 🎮\n<i>Premium Suite v2.0</i>",
        "account": "Cuenta",
        "user_id": "ID de Usuario",
        "wallet": "CARTERA",
        "coins": "Monedas",
        "status": "Estado",
        "unlimited": "👑 Ilimitado",
        "standard": "🪙 Estándar",
        "subscription": "SUSCRIPCIÓN",
        "plan": "Plan",
        "expires": "Expira",
        "lifetime": "👑 De por Vida",
        "never": "Nunca expira",
        "active": "✅ Activo",
        "none": "❌ Ninguno",
        "statistics": "ESTADÍSTICAS",
        "operations": "Operaciones",
        "member_since": "Miembro Desde",
        "select_feature": "⚡ Selecciona una función del menú",
        "account_tools": "HERRAMIENTAS",
        "cpm1_pass": "🔐 CPM1 Pass",
        "cpm2_pass": "🔐 CPM2 Pass",
        "conversion": "CONVERSIÓN",
        "cpm1_to_cpm2": "📀 CPM1 → CPM2 (Manual)",
        "cpm2_to_cpm2": "📀 CPM2 → CPM2 (Manual)",
        "premium": "PREMIUM",
        "api_vinyl": "🎨 Transferencia Vinyl API (1-Clic) ⚡",
        "garage": "MODS DE GARAJE",
        "unlock_all": "🔥 Desbloquear Todo",
        "body_mods": "🚗 Mods de Carrocería",
        "upload_zip": "📦 Subir ES3 Folder (ZIP)",
        "info": "INFORMACIÓN",
        "pricing": "💎 Precios y Planes",
        "contact": "📞 Contactar Admin",
        "language": "🌐 Idioma",
        "coin_farm": "🚗 Granja de Monedas",
        "rank": "🏆 Rango",
        "full_unlock": "🔥 DESBLOQUEO TOTAL",
        "individual": "🛠️ PARTES INDIVIDUALES",
        "save_file": "📦 GUARDAR ARCHIVO (ZIP)",
        "main_menu": "🔙 Menú Principal",
        "exit_garage": "❌ Salir del Garaje",
        "air_sus": "🚗 Solo Suspensión de Aire",
        "police": "🚓 Solo Mods de Policía",
        "bodykits": "🎨 Solo Bodykits",
        "mileage": "📉 Reinicio de Millaje",
        "front_bumper": "🔧 Quitar Paragolpes Delantero",
        "rear_bumper": "🔧 Quitar Paragolpes Trasero",
        "back_garage": "🔙 Volver al Garaje",
        "back": "🔙 Atrás",
        "cancel": "❌ Cancelar",
        "send_creds": "Envía credenciales como <code>email:password</code>",
        "connecting": "⏳ Conectando...",
        "select_src": "👇 Selecciona coche ORIGEN",
        "select_tgt": "👇 Selecciona coche DESTINO",
        "connected": "¡Conectado! Encontrado",
        "cars": "coches",
        "transfer_complete": "¡Transferencia Completa!",
        "transfer_failed": "Transferencia Fallida",
        "source": "Origen",
        "target": "Destino",
        "need_coins": "❌ Necesitas {amount} monedas. Tienes {have}.",
        "insufficient": "❌ Monedas insuficientes",
        "applying": "Aplicando {mod}...",
        "done": "Hecho",
        "total": "Total",
        "processed": "Procesado",
        "modified": "Modificado",
        "failed": "Fallido",
        "upload_es3": "📦 Envía tu carpeta ES3 como .zip",
        "sending_creds": "📧 Envía tu email CPM1",
        "farm_prompt": "🚗 <b>Granja de Monedas</b>\n\n📧 Envía tu email CPM2:",
        "farm_pass": "🔑 Envía tu contraseña CPM2:",
        "farm_running": "⏳ Iniciando granja...",
        "farm_done": "✅ ¡GRANJA COMPLETA!",
        "farm_start": "Inicio",
        "farm_earned": "Ganado",
        "farm_final": "Final",
        "farm_success": "Éxito",
        "rank_title": "🏆 SISTEMA DE RANGOS",
        "your_rank": "Tu Rango",
        "rank_list": "Rangos:\n🟢 CAYLAK: 10 ops/día\n🔵 DENEYIMLI: 20 ops/día\n🟣 USTA: 30 ops/día\n🟠 ELIT: 50 ops/día\n🔴 EFSANE: Ilimitado",
        "lang_saved": "✅ ¡Idioma guardado!",
    },
    "tr": {
        "lang_name": "🇹🇷 Türkçe",
        "select_lang": "🌐 Dil Seçin",
        "welcome": "🎮 <b>MARK CPM TOOL</b> 🎮\n<i>Premium Suite v2.0</i>",
        "account": "Hesap",
        "user_id": "Kullanıcı ID",
        "wallet": "CÜZDAN",
        "coins": "Coin",
        "status": "Durum",
        "unlimited": "👑 Sınırsız",
        "standard": "🪙 Standart",
        "subscription": "ABONELİK",
        "plan": "Plan",
        "expires": "Bitiş",
        "lifetime": "👑 Ömür Boyu",
        "never": "Süresiz",
        "active": "✅ Aktif",
        "none": "❌ Yok",
        "statistics": "İSTATİSTİK",
        "operations": "İşlem",
        "member_since": "Üyelik Tarihi",
        "select_feature": "⚡ Menüden bir özellik seçin",
        "account_tools": "HESAP ARAÇLARI",
        "cpm1_pass": "🔐 CPM1 Pass",
        "cpm2_pass": "🔐 CPM2 Pass",
        "conversion": "DÖNÜŞÜM",
        "cpm1_to_cpm2": "📀 CPM1 → CPM2 (Manuel)",
        "cpm2_to_cpm2": "📀 CPM2 → CPM2 (Manuel)",
        "premium": "PREMIUM ÖZELLİKLER",
        "api_vinyl": "🎨 API Vinil Transfer (Tek Tık) ⚡",
        "garage": "GARAJ MODLARI",
        "unlock_all": "🔥 Tümünü Aç",
        "body_mods": "🚗 Tam Gövde Modları",
        "upload_zip": "📦 ES3 Klasörü Yükle (ZIP)",
        "info": "BİLGİ",
        "pricing": "💎 Fiyatlar ve Planlar",
        "contact": "📞 Admin ile İletişim",
        "language": "🌐 Dil",
        "coin_farm": "🚗 Coin Farm",
        "rank": "🏆 Rütbe",
        "full_unlock": "🔥 TAM AÇ",
        "individual": "🛠️ BİREYSEL PARÇALAR",
        "save_file": "📦 DOSYAYI KAYDET (ZIP)",
        "main_menu": "🔙 Ana Menü",
        "exit_garage": "❌ Garajdan Çık",
        "air_sus": "🚗 Sadece Hava Süspansiyon",
        "police": "🚓 Sadece Polis Modları",
        "bodykits": "🎨 Sadece Bodykitler",
        "mileage": "📉 KM Sıfırlama",
        "front_bumper": "🔧 Ön Tampon Sök",
        "rear_bumper": "🔧 Arka Tampon Sök",
        "back_garage": "🔙 Garaja Dön",
        "back": "🔙 Geri",
        "cancel": "❌ İptal",
        "send_creds": "Kimlik bilgilerini <code>email:password</code> olarak gönder",
        "connecting": "⏳ Bağlanıyor...",
        "select_src": "👇 KAYNAK araç seç",
        "select_tgt": "👇 HEDEF araç seç",
        "connected": "Bağlandı! Bulundu",
        "cars": "araç",
        "transfer_complete": "Transfer Tamamlandı!",
        "transfer_failed": "Transfer Başarısız",
        "source": "Kaynak",
        "target": "Hedef",
        "need_coins": "❌ {amount} coin gerekli. Sende {have} var.",
        "insufficient": "❌ Yetersiz coin",
        "applying": "{mod} uygulanıyor...",
        "done": "Tamam",
        "total": "Toplam",
        "processed": "İşlenen",
        "modified": "Değiştirilen",
        "failed": "Başarısız",
        "upload_es3": "📦 ES3 klasörünü .zip olarak gönder",
        "sending_creds": "📧 CPM1 emailini gönder",
        "farm_prompt": "🚗 <b>Coin Farm</b>\n\n📧 CPM2 emailini gönder:",
        "farm_pass": "🔑 CPM2 şifreni gönder:",
        "farm_running": "⏳ Farm başlıyor...",
        "farm_done": "✅ FARM TAMAMLANDI!",
        "farm_start": "Başlangıç",
        "farm_earned": "Kazanılan",
        "farm_final": "Final",
        "farm_success": "Başarı",
        "rank_title": "🏆 RÜTBE SİSTEMİ",
        "your_rank": "Rütben",
        "rank_list": "Rütbeler:\n🟢 CAYLAK: 10 işlem/gün\n🔵 DENEYIMLI: 20 işlem/gün\n🟣 USTA: 30 işlem/gün\n🟠 ELIT: 50 işlem/gün\n🔴 EFSANE: Sınırsız",
        "lang_saved": "✅ Dil kaydedildi!",
    },
    "ru": {
        "lang_name": "🇷🇺 Русский",
        "select_lang": "🌐 Выберите язык",
        "welcome": "🎮 <b>MARK CPM TOOL</b> 🎮\n<i>Premium Suite v2.0</i>",
        "account": "Аккаунт",
        "user_id": "ID",
        "wallet": "КОШЕЛЁК",
        "coins": "Монеты",
        "status": "Статус",
        "unlimited": "👑 Безлимит",
        "standard": "🪙 Стандарт",
        "subscription": "ПОДПИСКА",
        "plan": "План",
        "expires": "Истекает",
        "lifetime": "👑 Навсегда",
        "never": "Никогда",
        "active": "✅ Активна",
        "none": "❌ Нет",
        "statistics": "СТАТИСТИКА",
        "operations": "Операции",
        "member_since": "С нами с",
        "select_feature": "⚡ Выберите функцию из меню",
        "account_tools": "ИНСТРУМЕНТЫ",
        "cpm1_pass": "🔐 CPM1 Pass",
        "cpm2_pass": "🔐 CPM2 Pass",
        "conversion": "КОНВЕРТАЦИЯ",
        "cpm1_to_cpm2": "📀 CPM1 → CPM2 (Вручную)",
        "cpm2_to_cpm2": "📀 CPM2 → CPM2 (Вручную)",
        "premium": "ПРЕМИУМ",
        "api_vinyl": "🎨 API Винил Трансфер (1 клик) ⚡",
        "garage": "МОДЫ ГАРАЖА",
        "unlock_all": "🔥 Разблокировать всё",
        "body_mods": "🚗 Все кузовные моды",
        "upload_zip": "📦 Загрузить ES3 папку (ZIP)",
        "info": "ИНФО",
        "pricing": "💎 Цены и планы",
        "contact": "📞 Связаться с админом",
        "language": "🌐 Язык",
        "coin_farm": "🚗 Фарм монет",
        "rank": "🏆 Ранг",
        "full_unlock": "🔥 ПОЛНАЯ РАЗБЛОКИРОВКА",
        "individual": "🛠️ ОТДЕЛЬНЫЕ ДЕТАЛИ",
        "save_file": "📦 СОХРАНИТЬ ФАЙЛ (ZIP)",
        "main_menu": "🔙 Главное меню",
        "exit_garage": "❌ Выйти из гаража",
        "air_sus": "🚗 Только пневмоподвеска",
        "police": "🚓 Только полицейские моды",
        "bodykits": "🎨 Только обвесы",
        "mileage": "📉 Сброс пробега",
        "front_bumper": "🔧 Снять передний бампер",
        "rear_bumper": "🔧 Снять задний бампер",
        "back_garage": "🔙 Назад в гараж",
        "back": "🔙 Назад",
        "cancel": "❌ Отмена",
        "send_creds": "Отправьте данные как <code>email:password</code>",
        "connecting": "⏳ Подключение...",
        "select_src": "👇 Выберите ИСХОДНУЮ машину",
        "select_tgt": "👇 Выберите ЦЕЛЕВУЮ машину",
        "connected": "Подключено! Найдено",
        "cars": "машин",
        "transfer_complete": "Трансфер завершён!",
        "transfer_failed": "Трансфер не удался",
        "source": "Источник",
        "target": "Цель",
        "need_coins": "❌ Нужно {amount} монет. У вас {have}.",
        "insufficient": "❌ Недостаточно монет",
        "applying": "Применение {mod}...",
        "done": "Готово",
        "total": "Всего",
        "processed": "Обработано",
        "modified": "Изменено",
        "failed": "Ошибок",
        "upload_es3": "📦 Отправьте ES3 папку как .zip",
        "sending_creds": "📧 Отправьте CPM1 email",
        "farm_prompt": "🚗 <b>Фарм монет</b>\n\n📧 Отправьте CPM2 email:",
        "farm_pass": "🔑 Отправьте CPM2 пароль:",
        "farm_running": "⏳ Фарм запускается...",
        "farm_done": "✅ ФАРМ ЗАВЕРШЁН!",
        "farm_start": "Старт",
        "farm_earned": "Заработано",
        "farm_final": "Итог",
        "farm_success": "Успех",
        "rank_title": "🏆 СИСТЕМА РАНГОВ",
        "your_rank": "Ваш ранг",
        "rank_list": "Ранги:\n🟢 CAYLAK: 10/день\n🔵 DENEYIMLI: 20/день\n🟣 USTA: 30/день\n🟠 ELIT: 50/день\n🔴 EFSANE: Безлимит",
        "lang_saved": "✅ Язык сохранён!",
    },
}

def load_langs():
    try:
        with open(LANG_FILE, "r") as f: return json.load(f)
    except: return {}

def save_langs(data):
    with open(LANG_FILE, "w") as f: json.dump(data, f, indent=4)

def get_user_lang(user_id):
    return load_langs().get(str(user_id), "en")

def set_user_lang(user_id, lang):
    data = load_langs()
    data[str(user_id)] = lang
    save_langs(data)

def T(user_id, key, **kwargs):
    lang = get_user_lang(user_id)
    template = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key)
    if not template:
        template = TRANSLATIONS["en"].get(key, key)
    try:
        return template.format(**kwargs) if kwargs else template
    except:
        return template

# ============================================================
# CAR NAMES
# ============================================================
CAR_NAMES_JSON = {
    "1":"BMW 135I","2":"VW scirocco","3":"BMW M5 2015","4":"OLD GWAGON","5":"Chevy camaro",
    "6":"subaru brz","7":"lexus lfa","8":"infinity g36","9":"subie stinkeye","10":"Ferrari f12",
    "11":"r34 skyline","12":"Evo 10","13":"ek9","14":"gtr r35","15":"audi rs4","17":"merc c63",
    "18":"lambo huracan","19":"merc amg gtr","20":"audi tt","21":"jeep Wrangler","22":"BMW m6",
    "23":"Hyundai Veloster","24":"Porsche panamera","25":"Bugatti Veyron","28":"Porsche Cayenne",
    "29":"Honda Fn2","30":"BMW M5 99's","31":"BMW M5 05's","32":"Koenigsegg Agera",
    "35":"Ford mustang shelby gt500","37":"Ford transit","39":"Dodge Charger 70's","40":"Corvette c7",
    "41":"McLaren P1","42":"Lambo Aventador","43":"Lexuc is300","44":"Lambo Veneno","45":"BMW M5 97's",
    "47":"S2000","48":"RX8","49":"Mk4 supra","51":"old Ferrari","53":"hakosuka gtr r31",
    "54":"BMW M5 80'S","55":"Hummer H1","56":"BMW M3 e93","57":"Cadillac CTS V","58":"Ferrari 458",
    "59":"Smart fourtwo","60":"Cadillac Escalade","61":"Mercedes E series","62":"Dodge Charger",
    "65":"Lambo Gallardo","66":"Chrysler 300c","70":"Scania Truck","74":"Peugeot 308","76":"BMW Z4",
    "77":"Mini Cooper","81":"Subaru Hawkeye","82":"Evo 8","85":"Ford Ranger","86":"BMW X5",
    "87":"Mercedes C series","88":"Iconic Bmw M3","89":"Hudson Hornet","99":"LADA",
    "100":"Russian car","101":"Ford Trailer","102":"Russian car","103":"BMW M4 f82","104":"BMW M5 F90",
    "105":"Dodge Challenger","106":"Old Mercedes E","107":"Audi R8 V10 old","108":"Audi quattro",
    "109":"Porsche 911 991","110":"Range Rover SVR","111":"New nsx","112":"Mercedes E class",
    "113":"Golf r mk7","114":"Mercedes S class","115":"Audi R8 V10 plus","116":"Mustang 5.0",
    "117":"Audi s7","118":"BMW X6","119":"Hummer Military","120":"Toyota Camry","121":"Toyota lc200",
    "123":"Mercedes gle","124":"Rolls Royce wraith","125":"Lambo Urus","126":"Gmc Sierra","127":"BMW M2",
    "128":"Nissan S15","129":"Rx7","130":"Ford Gt","131":"Nissan 240sx","132":"Russian car",
    "133":"Myvi Perodua m600","134":"toyota chaser","135":"audi rs6","136":"Mercedes E class",
    "137":"Honda fd2","138":"BMW i8","139":"Ford crown Victoria","140":"Toyota Ae86","141":"Dodge Viper",
    "142":"Mercedes c63","143":"Mercedes g63 new","145":"Nissan 350z","146":"Russian car",
    "147":"Honda fk8","148":"Fastback mustang","149":"Oldies car","150":"supra mk5","151":"toyota velfire",
    "152":"Russian car","153":"BMW M4 G82","154":"Toyota Hilux","155":"old f1","156":"r32 gtr",
    "157":"golf r mk5","158":"mazda mx5","159":"Lambo SVJ","160":"Old Dodge Challenger",
    "161":"jeep Cherokee","162":"McLaren 720s","163":"Mercedes convertible","164":"Dune buggy",
    "165":"new f1","166":"Corvette c8","167":"Dodge Ram","168":"Bentley Continental","169":"Ford Explorer",
    "170":"Peterbilt truck","171":"Scania truck","172":"Rolls Royce Cullinan","173":"Mercedes E class",
    "175":"Mercedes E class","176":"Chevy pickup","177":"Nissan s13","178":"Bugatti Chiron SS",
    "179":"Chevy","180":"Chevy pickup","181":"ford mustang old","182":"Drift truck hoonicorn",
    "183":"Drift mustang","184":"Mitsubishi Eclipse","185":"Chevy Impala","186":"Astro Van",
    "187":"Mazda Miata","188":"Porsche Gt3rs","189":"Ford Raptor","190":"Peugeot","191":"Bus 1",
    "192":"Ram Trx","193":"M3 Touring","194":"Mercedes Slr","195":"Bus 2","196":"dodge old charger",
    "197":"VW microbus","198":"Koenigsegg Jesko","199":"Corvette C6","200":"Dodge Durango",
    "201":"Mercedes Clk gtr","202":"Pagani Zonda","204":"Mercede Van","205":"Porsche rwb",
    "206":"Alfa Romeo Giulia","207":"Porsche Le mans","208":"Ford Bronco","209":"Lexus is300 2009",
    "210":"Corvette C5","211":"Audi Rs7","212":"6x6 Mercedes g63","213":"Nissan R33",
    "214":"Toyota Chaser mk2","215":"Chevy Tahoe","216":"McLaren Senna","217":"BMW X7",
    "218":"Toyota Crown","219":"VW Passat","220":"Fairlady Z","221":"Old nsx","222":"Porsche 918",
    "223":"DMC delorean","224":"Subaru Raptor eye","225":"Honda Delsol","226":"Fiat van","227":"Amg One",
    "228":"Audi Rs2","229":"Ferrari F40","230":"Land Rover","231":"Toyota lc250 old","232":"Kia Stinger",
    "233":"BMW i7","234":"Austin Martin","235":"Mustang","236":"RV","237":"Semi Truck",
    "238":"BMW M5","239":"Escalade","240":"Ford focus","241":"La Ferrari","242":"Camaro",
    "243":"Jeep gladiator","244":"Land Rover","245":"Toyota GR Yaris","248":"Russian Car",
    "249":"Maybach","250":"Porsche Carrera GT","252":"bmw","257":"M2","258":"Mercedes",
    "261":"new truck","264":"new Camry",
}

def get_car_name(car_id):
    return CAR_NAMES_JSON.get(str(car_id), f"Car {car_id}")

# ============================================================
# MEMORYPACK HELPERS
# ============================================================
def _derive_key_iv(local_id):
    if not local_id: return None, None
    prefix = local_id[:8]
    raw = (prefix + "12345678").encode("utf-8")[:16]
    return raw, raw

def _encrypt_value(value, local_id):
    key, iv = _derive_key_iv(local_id)
    if not key or not iv: return None
    raw = value.encode("utf-8")
    padding = 16 - len(raw) % 16
    raw += bytes([padding]) * padding
    return base64.b64encode(AES.new(key, AES.MODE_CBC, iv).encrypt(raw)).decode("utf-8")

def _json_unwrap(value):
    current = value
    for _ in range(4):
        if not isinstance(current, str): break
        try: current = json.loads(current)
        except: break
    return current

def _int_value(value, default=0):
    try: return int(value)
    except: return default

def _float_value(value):
    try:
        n = float(value)
        return n if math.isfinite(n) else 0.0
    except: return 0.0

def _uint32_value(value): return _int_value(value) & 0xFFFFFFFF
def _int64_value(value):
    n = _int_value(value)
    if n > 0x7FFFFFFFFFFFFFFF: n -= 0x10000000000000000
    if n < -0x8000000000000000: n = -0x8000000000000000
    return n

def _memorypack_string(value):
    encoded = value.encode("utf-8")
    if not encoded: return struct.pack("<i", 0)
    return struct.pack("<ii", ~len(encoded), len(value)) + encoded

def _vector3(value):
    if not isinstance(value, dict): return 0.0, 0.0, 0.0
    return (_float_value(value.get("x", value.get("X"))),
            _float_value(value.get("y", value.get("Y"))),
            _float_value(value.get("z", value.get("Z"))))

def _serialize_vinyl_item(item):
    position = _vector3(item.get("position"))
    scale_rotation = _vector3(item.get("scaleRotation", item.get("scale_rotation")))
    icon_position = _vector3(item.get("iconPosition", item.get("icon_position")))
    text = str(item.get("text") or "")
    color = _uint32_value(item.get("color"))
    packed_data = _int64_value(item.get("packedData"))
    return (b"\x06" + struct.pack("<9f", *position, *scale_rotation, *icon_position)
            + _memorypack_string(text) + struct.pack("<Iq", color, packed_data))

def _serialize_vinyl_list(items):
    return struct.pack("<i", len(items)) + b"".join(_serialize_vinyl_item(i) for i in items)

def _extract_vinyl_items(value):
    if isinstance(value, list): return [i for i in value if isinstance(i, dict)]
    if not isinstance(value, dict): return None
    if isinstance(value.get("allVynils"), list): return [i for i in value["allVynils"] if isinstance(i, dict)]
    if isinstance(value.get("oneVynil"), list): return [i for i in value["oneVynil"] if isinstance(i, dict)]
    if {"position", "scaleRotation", "iconPosition"} & set(value): return [value]
    return None

def _brotli_decompress(payload):
    if brotli is None: return None
    try: return brotli.decompress(payload)
    except: return None

def _extract_vinyl_raw_candidate(payload):
    direct = _read_memorypack_vinyl_list(payload, 0, len(payload))
    if direct is not None and direct[0] == len(payload): return payload, direct[1]
    if not payload: return None
    wrapped = _read_memorypack_vinyl_list(payload, 1, len(payload))
    if wrapped is None: return None
    remainder = len(payload) - wrapped[0]
    if remainder in (0, 4): return payload[1:wrapped[0]], wrapped[1]
    return None

def _normalize_cpm1_vinyl_field(value):
    items = _extract_vinyl_items(value)
    if items is not None: return _serialize_vinyl_list(items), len(items)
    if value in (None, "", []): return _serialize_vinyl_list([]), 0
    if not isinstance(value, str): return None
    try: decoded = base64.b64decode(value, validate=True)
    except: return None
    for candidate in (decoded, _brotli_decompress(decoded)):
        if not isinstance(candidate, (bytes, bytearray)): continue
        parsed = _extract_vinyl_raw_candidate(bytes(candidate))
        if parsed is not None: return parsed
    return None

def _instance_id_from_car(car):
    texts = car.get("texts")
    if isinstance(texts, list):
        for index in (2, 1, 0):
            if index < len(texts):
                value = str(texts[index] or "").strip()
                if value: return value
    return ""

def _normalize_cpm1_car(raw_car, index, names):
    if not isinstance(raw_car, dict): return None
    car_id = _int_value(raw_car.get("CarID"))
    if car_id <= 0: return None
    vinyls = _normalize_cpm1_vinyl_field(raw_car.get("Vynils"))
    window = _normalize_cpm1_vinyl_field(raw_car.get("WindowVinyls"))
    supported = vinyls is not None and window is not None
    return {"id": car_id, "index": index, "name": names.get(str(car_id), f"Car {car_id}"),
            "instance_id": _instance_id_from_car(raw_car), "transferable": supported,
            "style_transferable": supported,
            "vinyls": vinyls[1] if vinyls else -1, "window": window[1] if window else -1,
            "vinyls_raw": vinyls[0] if vinyls else None, "window_raw": window[0] if window else None}

def _memorypack_xor_key(local_id):
    chars = list(local_id or "")
    if len(chars) >= 7: chars[6], chars[4] = chars[4], chars[6]
    if len(chars) >= 9: chars.pop(8)
    if chars: chars.append(chars[0])
    return "".join(chars).encode("utf-8")

_B64_TEXT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\r\n"

def _decode_current_memorypack(value, local_id):
    if not isinstance(value, dict) or value.get("code") != 1 or not isinstance(value.get("data"), str):
        return None
    if brotli is None: return None
    try:
        encrypted = base64.b64decode("".join(value["data"].split()), validate=True)
        for _ in range(2):
            if not encrypted or any(chr(b) not in _B64_TEXT for b in encrypted[:256]): break
            try: encrypted = base64.b64decode(encrypted.translate(None, b"\r\n"), validate=True)
            except: break
        xor_key = _memorypack_xor_key(local_id)
        if not xor_key: return None
        packed = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(encrypted))
        return brotli.decompress(packed)
    except: return None

def _read_memorypack_string(payload, offset, end):
    if offset + 4 > end: return None
    marker = struct.unpack_from("<i", payload, offset)[0]
    offset += 4
    if marker == -1 or marker == 0: return offset
    if marker > 0: byte_count = marker * 2
    else:
        byte_count = ~marker
        if offset + 4 > end: return None
        offset += 4
    if byte_count < 0 or offset + byte_count > end: return None
    return offset + byte_count

def _decode_memorypack_string_at(payload, offset, end):
    if offset + 4 > end: return None
    marker = struct.unpack_from("<i", payload, offset)[0]
    cursor = offset + 4
    if marker in (-1, 0): return cursor, ""
    if marker > 0:
        byte_count = marker * 2
        if cursor + byte_count > end: return None
        try: return cursor + byte_count, payload[cursor:cursor+byte_count].decode("utf-16-le")
        except: return None
    byte_count = ~marker
    if cursor + 4 + byte_count > end: return None
    char_count = struct.unpack_from("<i", payload, cursor)[0]
    cursor += 4
    try: value = payload[cursor:cursor+byte_count].decode("utf-8")
    except: return None
    if char_count >= 0 and len(value) != char_count: return None
    return cursor + byte_count, value

def _read_memorypack_vinyl(payload, offset, end):
    if offset >= end: return None
    member_count = payload[offset]; offset += 1
    if member_count == 255: return offset
    if member_count != 6 or offset + 36 > end: return None
    values = struct.unpack_from("<9f", payload, offset)
    if not all(math.isfinite(v) and abs(v) < 1_000_000 for v in values): return None
    offset += 36
    offset = _read_memorypack_string(payload, offset, end)
    if offset is None or offset + 12 > end: return None
    return offset + 12

def _read_memorypack_vinyl_list(payload, offset, end):
    if offset + 4 > end: return None
    count = struct.unpack_from("<i", payload, offset)[0]
    offset += 4
    if count == -1: return offset, 0
    if count < 0 or count > 2000: return None
    for _ in range(count):
        offset = _read_memorypack_vinyl(payload, offset, end)
        if offset is None: return None
    return offset, count

def _read_memorypack_int_list(payload, offset, end):
    if offset + 4 > end: return None
    count = struct.unpack_from("<i", payload, offset)[0]
    offset += 4
    if count == -1: return offset
    if count < 0 or count > 1000 or offset + count * 4 > end: return None
    return offset + count * 4

def _read_memorypack_installed_body_kits(payload, offset, end):
    if offset >= end: return None
    member_count = payload[offset]; offset += 1
    if member_count == 255: return offset
    if member_count != 10 or offset + 32 > end: return None
    offset += 32
    trims_start = offset
    offset = _read_memorypack_int_list(payload, offset, end)
    if offset is None: offset = _read_memorypack_string(payload, trims_start, end)
    if offset is None or offset + 4 > end: return None
    return offset + 4

def _read_memorypack_body_kit_colors(payload, offset, end):
    if offset >= end: return None
    member_count = payload[offset]; offset += 1
    if member_count == 255: return offset
    if member_count != 1 or offset + 4 > end: return None
    count = struct.unpack_from("<i", payload, offset)[0]; offset += 4
    if count == -1: return offset
    if count < 0 or count > 128: return None
    for _ in range(count):
        if offset >= end: return None
        item_members = payload[offset]; offset += 1
        if item_members == 255: continue
        if item_members not in (2, 3) or offset + 12 > end: return None
        offset += 12
    return offset

def _read_memorypack_colors(payload, offset, end):
    if offset >= end: return None
    member_count = payload[offset]; offset += 1
    if member_count == 255: return offset
    if member_count != 8 or offset + 32 > end: return None
    offset += 32
    return _read_memorypack_body_kit_colors(payload, offset, end)

def _read_memorypack_bought_body_kits(payload, offset, end):
    if offset >= end: return None
    member_count = payload[offset]; offset += 1
    if member_count == 255: return offset
    if member_count != 10: return None
    for _ in range(10):
        offset = _read_memorypack_int_list(payload, offset, end)
        if offset is None: return None
    return offset

def _memorypack_car_offsets(payload):
    if len(payload) < 4: return None
    expected_count = struct.unpack_from("<i", payload, 0)[0]
    if expected_count == 0: return []
    if expected_count < 0 or expected_count > 5000: return None
    known_ids = {int(c) for c in CAR_NAMES_JSON if str(c).isdigit()}
    known, broad = [], []
    for offset in range(4, len(payload) - 5):
        if payload[offset] != 9 or payload[offset + 5] not in (10, 255): continue
        car_id = struct.unpack_from("<i", payload, offset + 1)[0]
        if 0 < car_id <= 5000:
            broad.append((offset, car_id))
            if car_id in known_ids: known.append((offset, car_id))
    if len(known) == expected_count: return known
    if len(broad) == expected_count: return broad
    confirmed = []
    for offset, car_id in broad:
        installed_end = _read_memorypack_installed_body_kits(payload, offset + 5, len(payload))
        if installed_end is None: continue
        if _read_memorypack_colors(payload, installed_end, len(payload)) is None: continue
        confirmed.append((offset, car_id))
    if len(confirmed) == expected_count: return confirmed
    if broad and len(confirmed) == len(broad) and _car_records_span_payload(payload, confirmed):
        return confirmed
    return None

def _car_records_span_payload(payload, records):
    starts = [o for o, _ in records] + [len(payload)]
    for i in range(len(records)):
        start, end = starts[i], starts[i+1]
        for offset in range(start + 5, max(start + 6, end - 7)):
            first = _read_memorypack_vinyl_list(payload, offset, end)
            if first is None: continue
            second = _read_memorypack_vinyl_list(payload, first[0], end)
            if second is not None and second[0] == end: break
        else: return False
    return True

def _find_memorypack_car_instance(payload, start, vinyl_offset):
    strict = re.compile(r"^[A-Za-z]{2}\d{3,}_[A-Za-z]{2}\d{2,}_\d{2,}$")
    fallback = None
    for offset in range(start + 5, max(start + 5, vinyl_offset - 3)):
        decoded = _decode_memorypack_string_at(payload, offset, vinyl_offset)
        if decoded is None: continue
        end, text = decoded
        if not (8 <= len(text) <= 80 and text.count("_") >= 2 and any(c.isdigit() for c in text)): continue
        raw = payload[offset:end]
        if strict.fullmatch(text): return text, raw
        if fallback is None and re.fullmatch(r"[A-Za-z0-9_-]+", text): fallback = (text, raw)
    return fallback

def _extract_memorypack_style_fields(payload, start, end, vinyl_offset, instance_raw):
    installed_start = start + 5
    installed_end = _read_memorypack_installed_body_kits(payload, installed_start, end)
    if installed_end is None: return None
    colors_start = installed_end
    colors_end = _read_memorypack_colors(payload, colors_start, end)
    if colors_end is None: return None
    instance_start = payload.find(instance_raw, colors_end, vinyl_offset)
    if instance_start < 0: return None
    instance_end = instance_start + len(instance_raw)
    bought_candidates = [o for o in range(instance_end, vinyl_offset)
                          if _read_memorypack_bought_body_kits(payload, o, vinyl_offset) == vinyl_offset]
    if not bought_candidates: return None
    bought_start = max(bought_candidates)
    if not (colors_end < instance_start < instance_end < bought_start < vinyl_offset): return None
    return {2: payload[bought_start:vinyl_offset], 3: payload[colors_start:colors_end],
            4: payload[instance_end:bought_start], 5: payload[colors_end:instance_start],
            6: payload[installed_start:installed_end]}

def _parse_memorypack_cloud_vinyls(value, local_id):
    payload = _decode_current_memorypack(value, local_id)
    if payload is None: return None
    records = _memorypack_car_offsets(payload)
    if records is None: return None
    result = []
    for index, (start, car_id) in enumerate(records):
        end = records[index+1][0] if index+1 < len(records) else len(payload)
        match = None
        for offset in range(start + 5, max(start + 5, end - 7)):
            first = _read_memorypack_vinyl_list(payload, offset, end)
            if first is None: continue
            second = _read_memorypack_vinyl_list(payload, first[0], end)
            if second is not None and second[0] == end:
                c = (first[1], second[1], offset, first[0])
                if match is None or (c[0]+c[1], c[2]) > (match[0]+match[1], match[2]): match = c
        car = {"index": index, "id": car_id, "vinyls": match[0] if match else -1,
               "window": match[1] if match else -1, "transferable": False,
               "fingerprint": hashlib.sha256(payload[start:end]).hexdigest()}
        if match is not None:
            instance = _find_memorypack_car_instance(payload, start, match[2])
            if instance is not None:
                iid, iraw = instance
                style = _extract_memorypack_style_fields(payload, start, end, match[2], iraw)
                car.update({"instance_id": iid, "car_id_raw": payload[start+1:start+5],
                            "instance_raw": iraw, "vinyls_raw": payload[match[2]:match[3]],
                            "window_raw": payload[match[3]:end], "style_fields": style,
                            "style_transferable": style is not None, "transferable": True})
        result.append(car)
    return result

def _parse_cpm1_memorypack_vinyls(payload):
    records = _memorypack_car_offsets(payload)
    if records is None: return None
    result = []
    for index, (start, car_id) in enumerate(records):
        end = records[index+1][0] if index+1 < len(records) else len(payload)
        match = None
        for offset in range(start + 5, end - 10):
            first = _read_memorypack_vinyl_list(payload, offset, end)
            if first is None: continue
            second = _read_memorypack_vinyl_list(payload, first[0], end)
            if second is not None:
                c = (first[1], second[1], offset, first[0], second[0])
                if match is None or (c[0]+c[1]) > (match[0]+match[1]): match = c
        transferable = match is not None
        result.append({"id": car_id, "index": index, "name": get_car_name(car_id),
                       "transferable": transferable, "style_transferable": transferable,
                       "vinyls": match[0] if match else -1, "window": match[1] if match else -1,
                       "vinyls_raw": payload[match[2]:match[3]] if match else None,
                       "window_raw": payload[match[3]:match[4]] if match else None})
    return result

# ============================================================
# COIN FARM (PhoenixCrypto)
# ============================================================
class PhoenixCrypto:
    def __init__(self, uid):
        self.key = (uid[:8] + KEY_ADD).encode()[:16]
        self.iv = (uid[:8] + IV_ADD).encode()[:16]
    def encrypt(self, text):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(pad(str(text).encode(), 16))).decode()
    def decrypt(self, text):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            return unpad(cipher.decrypt(base64.b64decode(text)), 16).decode()
        except: return None

async def farm_login_async(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={CPM2_API_KEY}"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:
        async with s.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=aiohttp.ClientTimeout(total=20)) as r:
            data = await r.json()
            if "idToken" in data: return data["idToken"], data["localId"]
    return None, None

async def farm_get_coins(token, uid):
    crypto = PhoenixCrypto(uid)
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    url = CF_BASE + "/GetCoins24_1"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:
        async with s.post(url, headers=headers, json={"data": None}) as r:
            if r.status == 200:
                result = await r.json()
                rd = result.get("result")
                if isinstance(rd, dict) and "data" in rd:
                    dec = crypto.decrypt(rd["data"])
                    if dec and dec.isdigit(): return int(dec)
    return 0

async def farm_coins(token, uid):
    crypto = PhoenixCrypto(uid)
    total, success, ops = 0, 0, 0
    combos = [(c, p, g) for c in range(6) for p in range(1, 4) for g in range(2)]
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:
        for c, p, g in combos:
            enc = crypto.encrypt(f"{c},{p},{g}")
            headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
            url = CF_BASE + "/SetDragRacing23_1"
            try:
                async with s.post(url, headers=headers, data=json.dumps({"data": enc}), timeout=aiohttp.ClientTimeout(total=30)) as r:
                    if r.status == 200:
                        text = await r.text()
                        try: result = json.loads(text).get("result")
                        except: result = None
                        coins = 0
                        if isinstance(result, str):
                            try:
                                p2 = json.loads(result)
                                if isinstance(p2, list) and len(p2) >= 2:
                                    dec = crypto.decrypt(p2[1]) if isinstance(p2[1], str) else None
                                    if dec and dec.isdigit(): coins = int(dec)
                            except: pass
                        elif isinstance(result, list) and len(result) >= 2:
                            dec = crypto.decrypt(result[1]) if isinstance(result[1], str) else None
                            if dec and dec.isdigit(): coins = int(dec)
                        if coins > 0:
                            total += coins
                            success += 1
                        ops += 1
            except: ops += 1
            await asyncio.sleep(0.05)
    return success, ops, total

# ============================================================
# API HELPERS
# ============================================================
async def firebase_verify_password(email, password, api_key, session=None):
    if not api_key: return {"error": {"message": "NO_API_KEY"}}
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={api_key}"
    async def request(s):
        try:
            async with s.post(url, json={"email": email, "password": password, "returnSecureToken": True},
                              timeout=aiohttp.ClientTimeout(total=15)) as r:
                try: data = await r.json(content_type=None)
                except: return {"error": {"message": "SERVICE_UNAVAILABLE", "transient": True}}
                if r.status == 429 or r.status >= 500:
                    return {"error": {"message": "SERVICE_UNAVAILABLE", "transient": True}}
                return data
        except: return {"error": {"message": "CONNECTION_ERROR", "transient": True}}
    if session: return await request(session)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as own: return await request(own)

def _cpm1_function_bases():
    seen, result = set(), []
    for b in (CPM1_API_BASE, *CPM1_FALLBACK_BASES):
        b = str(b or "").strip().rstrip("/")
        if b and b not in seen: seen.add(b); result.append(b)
    return tuple(result)

async def _call_cpm1_function(function_name, id_token, local_id, session):
    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
    encrypted_payload = _encrypt_value(json.dumps({}), local_id)
    if not encrypted_payload: return None, "ENCRYPT_FAILED"
    last_error = ""
    for base in _cpm1_function_bases():
        try:
            async with session.post(f"{base}/{function_name}", json={"data": encrypted_payload},
                                    headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as r:
                try: body = await r.json(content_type=None)
                except: body = await r.text()
                if r.status != 200:
                    last_error = f"{function_name}@{base}:HTTP_{r.status}"; continue
                if not isinstance(body, dict) or "result" not in body:
                    last_error = f"{function_name}@{base}:BAD_BODY"; continue
                return _json_unwrap(body.get("result")), ""
        except Exception as e:
            last_error = f"{function_name}@{base}:{type(e).__name__}"
    return None, last_error

async def _read_cpm1_current_cloud(id_token, local_id, session):
    raw, error = await _call_cpm1_function(CPM1_CARS_FUNCTION, id_token, local_id, session)
    if error: return None, error
    if not isinstance(raw, list): return None, "INVALID_RESPONSE"
    names = {k: v for k, v in CAR_NAMES_JSON.items()}
    cars = [n for i, c in enumerate(raw) if (n := _normalize_cpm1_car(c, i, names)) is not None]
    if not cars: return None, "EMPTY"
    if any(c.get("style_transferable") for c in cars): return cars, ""
    return None, "NO_SUPPORTED_VINYLS"

async def _read_cpm1_rtdb(id_token, local_id, session):
    headers = {"Authorization": f"Bearer {id_token}"}
    paths = [f"/users/{local_id}/OneCar.json", f"/OneCar/{local_id}.json",
             f"/users/{local_id}/cars.json", f"/users/{local_id}/garage.json", f"/cars/{local_id}.json"]
    for path in paths:
        url = f"{CPM1_DATABASE_URL}{path}"
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as r:
                text = await r.text()
                if r.status == 200 and text and text.strip() != "null":
                    try: value = json.loads(text)
                    except: value = text.strip().strip('"')
                    if isinstance(value, str) and len(value) > 10:
                        try: return base64.b64decode(value), ""
                        except: return None, "BASE64_ERROR"
                    if value and value != "null": return None, f"UNEXPECTED:{type(value).__name__}"
                elif r.status == 401: return None, "AUTH_EXPIRED"
        except: pass
    return None, "NOT_FOUND"

async def open_cpm1_cloud_session(email, password):
    result = {"cars": None, "error": "", "email": email, "password": password}
    auth = await firebase_verify_password(email, password, CPM1_API_KEY)
    if "error" in auth:
        result["error"] = str(auth["error"].get("message", "AUTH_ERROR")); return result
    id_token, local_id = auth.get("idToken"), auth.get("localId")
    if not id_token or not local_id:
        result["error"] = "INVALID_AUTH"; return result
    result["local_id"] = local_id; result["id_token"] = id_token
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        cars, err = await _read_cpm1_current_cloud(id_token, local_id, session)
        if cars is not None:
            result["cars"] = cars; result["cloud_source"] = "callable"; return result
        raw, rtdb_err = await _read_cpm1_rtdb(id_token, local_id, session)
        if raw is not None:
            legacy = _parse_cpm1_memorypack_vinyls(raw)
            if legacy is not None:
                result["cars"] = legacy; result["cloud_source"] = "rtdb"; return result
    result["error"] = "CPM1_UNSUPPORTED"
    return result

async def _call_function(function_name, id_token, local_id):
    encrypted_payload = _encrypt_value(json.dumps({}), local_id)
    if not encrypted_payload: return False, None
    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as s:
            async with s.post(f"{CPM2_API_BASE}/{function_name}", json={"data": encrypted_payload},
                              headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as r:
                try: body = await r.json(content_type=None)
                except: return False, None
                if r.status != 200 or not isinstance(body, dict) or "result" not in body: return False, None
                result = body.get("result")
                if isinstance(result, str):
                    try: result = json.loads(result)
                    except: pass
                return True, result
    except: return False, None

async def _call_function_payload(function_name, id_token, payload, session):
    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
    try:
        async with session.post(f"{CPM2_API_BASE}/{function_name}", json={"data": payload},
                                headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as r:
            try: body = await r.json(content_type=None)
            except: return False, None
            if r.status != 200 or not isinstance(body, dict) or "result" not in body: return False, body
            result = body.get("result")
            if isinstance(result, str):
                try:
                    parsed = json.loads(result)
                    if parsed is not None: result = parsed
                except: pass
            err = _function_result_error_code(result)
            if err is not None: return False, result
            return True, result
    except: return False, None

def _function_result_error_code(result):
    if isinstance(result, (int, float)) and not isinstance(result, bool):
        return None if result == 1 else int(result) if float(result).is_integer() else str(result)
    if isinstance(result, str) and result.strip().lstrip("-").isdigit():
        n = int(result.strip()); return None if n == 1 else n
    if not isinstance(result, dict): return None
    code = result.get("code")
    if code is not None:
        try: nc = int(code)
        except: nc = str(code)
        if nc != 1: return nc
    if result.get("success") is False: return "success=false"
    if result.get("error"): return str(result["error"])
    return None

async def _read_raw_cars(id_token, local_id):
    global _cars_function_name
    if _cars_function_name:
        try:
            ok, value = await _call_function(_cars_function_name, id_token, local_id)
            if ok: return value
        except: pass
    for fn in CPM2_CARS_FUNCTION_CANDIDATES:
        try:
            ok, value = await _call_function(fn, id_token, local_id)
            if ok:
                _cars_function_name = fn
                return value
        except: continue
    return None

async def _authenticate_cpm2(email, password, session):
    auth = await firebase_verify_password(email, password, CPM2_API_KEY, session=session)
    id_token = str(auth.get("idToken") or "")
    local_id = str(auth.get("localId") or "")
    error = str((auth.get("error") or {}).get("message") or "AUTH_FAILED")
    return id_token, local_id, "" if id_token and local_id else error

async def open_cloud_vinyl_session(email, password):
    result = {"cars": None, "error": "", "email": email, "password": password}
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=25)) as session:
            id_token, local_id, err = await _authenticate_cpm2(email, password, session)
            if err:
                result["error"] = err; return result
            value = await _read_raw_cars(id_token, local_id)
        if value is None:
            result["error"] = "CARS_UNAVAILABLE"; return result
        cars = _parse_memorypack_cloud_vinyls(value, local_id)
        if cars is None:
            result["error"] = "VINYL_SCHEMA_UNSUPPORTED"; return result
        result["cars"] = [{**c, "name": get_car_name(c["id"])} for c in cars]
    except Exception as e:
        logging.warning(f"CPM2 session error: {e}")
        result["error"] = "CONNECTION_ERROR"
    return result

def _encode_save_car_fields(target, donor, local_id, mode="vinyl"):
    values = {0: bytes(target["car_id_raw"]), 1: bytes(target["instance_raw"]),
              7: bytes(donor["vinyls_raw"]), 8: bytes(donor["window_raw"])}
    if mode == "style":
        style = donor.get("style_fields")
        if not isinstance(style, dict) or any(k not in style for k in range(2, 7)):
            raise ValueError("STYLE_SCHEMA_UNSUPPORTED")
        values.update({k: bytes(style[k]) for k in range(2, 7)})
    elif mode != "vinyl":
        raise ValueError("TRANSFER_MODE_INVALID")
    fields = tuple(sorted(values.items()))
    serialized = bytearray(struct.pack("<i", len(fields)))
    for key, field in fields:
        serialized.extend(struct.pack("<Hi", key, len(field)))
        serialized.extend(field)
    xor_key = _memorypack_xor_key(local_id)
    if brotli is None or not xor_key: raise ValueError("MEMORYPACK_UNAVAILABLE")
    packed = brotli.compress(bytes(serialized))
    encrypted = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(packed))
    return base64.b64encode(encrypted).decode("ascii")

async def execute_api_vinyl_transfer(cpm1_email, cpm1_password, cpm2_email, cpm2_password,
                                      cpm1_car_index, cpm2_car_index):
    result = {"sent": 0, "verified": 0, "total": 1, "error": ""}
    donor_snap = await open_cpm1_cloud_session(cpm1_email, cpm1_password)
    if donor_snap.get("error"):
        result["error"] = f"CPM1 Error: {donor_snap['error']}"; return result
    target_snap = await open_cloud_vinyl_session(cpm2_email, cpm2_password)
    if target_snap.get("error"):
        result["error"] = f"CPM2 Error: {target_snap['error']}"; return result
    donor_cars = {int(c["index"]): c for c in (donor_snap.get("cars") or [])}
    target_cars = {int(c["index"]): c for c in (target_snap.get("cars") or [])}
    donor_car = donor_cars.get(cpm1_car_index)
    target_car = target_cars.get(cpm2_car_index)
    if not donor_car or not donor_car.get("style_transferable"):
        result["error"] = "Source car is not transferable."; return result
    if not target_car or not target_car.get("transferable"):
        result["error"] = "Target car is not transferable."; return result
    try:
        if not isinstance(donor_car.get("vinyls_raw"), (bytes, bytearray)):
            result["error"] = "Source vinyls unavailable."; return result
        if not isinstance(donor_car.get("window_raw"), (bytes, bytearray)):
            result["error"] = "Source window vinyls unavailable."; return result
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=40)) as session:
            id_token, local_id, err = await _authenticate_cpm2(cpm2_email, cpm2_password, session)
            if err:
                result["error"] = f"CPM2 Auth Failed: {err}"; return result
            payload = _encode_save_car_fields(target_car, donor_car, local_id, mode="vinyl")
            ok, save_resp = await _call_function_payload(CPM2_SAVE_CAR_FUNCTION, id_token, payload, session)
            if not ok:
                result["error"] = "Save rejected by server."; return result
            result["sent"] = 1
            expected_iid = str(target_car.get("instance_id"))
            for attempt in range(5):
                if attempt: await asyncio.sleep(float(attempt))
                verified_val = await _read_raw_cars(id_token, local_id)
                verified_cars = _parse_memorypack_cloud_vinyls(verified_val, local_id)
                if verified_cars is None: continue
                for c in verified_cars:
                    if str(c.get("instance_id")) == expected_iid and c.get("vinyls_raw") == donor_car.get("vinyls_raw"):
                        result["verified"] = 1; break
                if result["verified"] == 1: break
            if result["verified"] != 1:
                result["error"] = "Transfer sent but verification pending."
            return result
    except Exception as e:
        result["error"] = f"Exception: {e}"; return result

# ============================================================
# COIN / SUBSCRIPTION / STATS
# ============================================================
def load_coins():
    try:
        with open(COIN_FILE, "r") as f: return json.load(f)
    except: return {}

def save_coins(data):
    with open(COIN_FILE, "w") as f: json.dump(data, f, indent=4)

def get_user_coins(user_id):
    return load_coins().get(str(user_id), {"coins": 0}).get("coins", 0)

def is_unlimited(user_id):
    return load_coins().get(str(user_id), {"unlimited": False}).get("unlimited", False)

def _ensure_user(data, sid):
    if sid not in data:
        data[sid] = {"coins": 0, "unlimited": False, "subscribed": False, "expiry": None}
    if "subscribed" not in data[sid]: data[sid]["subscribed"] = False
    if "expiry" not in data[sid]: data[sid]["expiry"] = None

def is_subscribed(user_id):
    data = load_coins()
    entry = data.get(str(user_id), {})
    expiry_str = entry.get("expiry")
    if expiry_str:
        try:
            if datetime.datetime.strptime(expiry_str, "%Y-%m-%d").date() < datetime.date.today():
                return False
        except: pass
    return entry.get("unlimited", False) or entry.get("subscribed", False)

def set_subscribed(user_id, status, days=0):
    data = load_coins(); sid = str(user_id)
    _ensure_user(data, sid)
    data[sid]["subscribed"] = status
    if days > 0:
        data[sid]["expiry"] = (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    else:
        data[sid]["expiry"] = None; data[sid]["subscribed"] = False
    save_coins(data)

def deduct_coins(user_id, amount):
    data = load_coins(); sid = str(user_id)
    _ensure_user(data, sid)
    if not data[sid]["unlimited"]: data[sid]["coins"] = max(0, data[sid]["coins"] - amount)
    save_coins(data)

def add_coins(user_id, amount):
    data = load_coins(); sid = str(user_id)
    if sid not in data: data[sid] = {"coins": 0, "unlimited": False, "subscribed": False, "expiry": None}
    data[sid]["coins"] += amount; save_coins(data)

def set_coins(user_id, amount):
    data = load_coins(); sid = str(user_id)
    if sid not in data: data[sid] = {"coins": 0, "unlimited": False, "subscribed": False, "expiry": None}
    data[sid]["coins"] = amount; save_coins(data)

def set_unlimited(user_id, status):
    data = load_coins(); sid = str(user_id)
    if sid not in data: data[sid] = {"coins": 0, "unlimited": False, "subscribed": False, "expiry": None}
    data[sid]["unlimited"] = status; save_coins(data)

def _load_stats():
    try:
        with open(STATS_FILE, "r") as f: return json.load(f)
    except: return {}

def _save_stats(data):
    with open(STATS_FILE, "w") as f: json.dump(data, f, indent=4)

def get_user_stats(user_id):
    stats = _load_stats(); sid = str(user_id)
    if sid not in stats:
        stats[sid] = {"operations": 0, "daily": 0, "last_date": "", "member_since": datetime.date.today().strftime("%Y-%m-%d")}
        _save_stats(stats)
    # Reset daily
    today = datetime.date.today().strftime("%Y-%m-%d")
    if stats[sid].get("last_date") != today:
        stats[sid]["daily"] = 0
        stats[sid]["last_date"] = today
        _save_stats(stats)
    return stats[sid]

def log_operation(user_id):
    stats = _load_stats(); sid = str(user_id)
    today = datetime.date.today().strftime("%Y-%m-%d")
    if sid not in stats:
        stats[sid] = {"operations": 0, "daily": 0, "last_date": today, "member_since": today}
    if stats[sid].get("last_date") != today:
        stats[sid]["daily"] = 0
        stats[sid]["last_date"] = today
    stats[sid]["operations"] = stats[sid].get("operations", 0) + 1
    stats[sid]["daily"] = stats[sid].get("daily", 0) + 1
    _save_stats(stats)

def get_user_rank(user_id):
    stats = get_user_stats(user_id)
    return get_rank(stats.get("operations", 0))

# ============================================================
# ES3 ENCRYPT / DECRYPT (WITH GZIP FIX)
# ============================================================
def apply_pkcs7(data, block_size=16):
    padding = block_size - (len(data) % block_size)
    return data + bytes([padding] * padding)

def remove_pkcs7(data):
    pl = data[-1]
    if pl < 1 or pl > 16: raise ValueError("Bad padding")
    if data[-pl:] != bytes([pl]) * pl: raise ValueError("Bad padding")
    return data[:-pl]

def decrypt_es3(file_data, password):
    if len(file_data) < 16: raise ValueError("Too short")
    iv = file_data[:16]; encrypted = file_data[16:]
    key = PBKDF2(password.encode(), iv, dkLen=16, count=100, hmac_hash_module=SHA1)
    decrypted = remove_pkcs7(AES.new(key, AES.MODE_CBC, iv=iv).decrypt(encrypted))
    # ✅ GZIP FIX - root cause ng failed mileage reset
    if len(decrypted) > 2 and decrypted[0] == 0x1f and decrypted[1] == 0x8b:
        try: decrypted = gzip.decompress(decrypted)
        except: pass
    return decrypted

def encrypt_es3(plain_data, password):
    iv = Random.get_random_bytes(16)
    key = PBKDF2(password.encode(), iv, dkLen=16, count=100, hmac_hash_module=SHA1)
    return iv + AES.new(key, AES.MODE_CBC, iv=iv).encrypt(apply_pkcs7(plain_data))

def build_es3_password(es3_first3, local_id): return es3_first3 + local_id[:3]

def decode_es3_filename(name):
    try:
        padding = len(name) % 4
        if padding: name += "=" * (4 - padding)
        return base64.b64decode(name).decode("utf-8")
    except: return name

def get_actual_es3_folder(extract_dir):
    items = os.listdir(extract_dir)
    if len(items) == 1:
        sp = os.path.join(extract_dir, items[0])
        if os.path.isdir(sp): return sp
    return extract_dir

def generate_session_cpm1(es3_first3, email, password):
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={CPM1_API_KEY}"
    try:
        r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True,
                                     "clientType": "CLIENT_TYPE_ANDROID"},
                          headers={"Content-Type": "application/json"}, timeout=20)
        r.raise_for_status()
        lid = r.json().get("localId")
        return es3_first3 + lid[:3] if lid else es3_first3 + "ERR"
    except: return es3_first3 + "ERR"

def generate_session_cpm2(es3_first3, email, password):
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={CPM2_API_KEY}"
    try:
        r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True,
                                     "clientType": "CLIENT_TYPE_ANDROID"},
                          headers={"Content-Type": "application/json"}, timeout=20)
        r.raise_for_status()
        lid = r.json().get("localId")
        return es3_first3 + lid[:3] if lid else es3_first3 + "ERR"
    except: return es3_first3 + "ERR"

def login_request(email, password, api_key):
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={api_key}"
    return requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}).json()

def update_request(id_token, api_key, new_email=None, new_password=None):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
    payload = {"idToken": id_token, "returnSecureToken": True}
    if new_email: payload["email"] = new_email
    if new_password: payload["password"] = new_password
    return requests.post(url, json=payload).json()

# ============================================================
# UNLOCK FUNCTIONS (WORKING PATTERNS FROM TURKISH BOT)
# ============================================================
def apply_mileage_reset(text):
    """✅ Working pattern: matches any number with [\d.]+"""
    return re.sub(r'"Mileage"\s*:\s*[\d.]+', '"Mileage" : 0', text)

def apply_remove_front_bumper(text):
    """✅ Working pattern: [^,}]+? matches value until comma/brace"""
    return re.sub(r'"FrontBumperId"\s*:\s*[^,}]+?', '"FrontBumperId" : -1', text)

def apply_remove_rear_bumper(text):
    """✅ Working pattern"""
    return re.sub(r'"RearBumperId"\s*:\s*[^,}]+?', '"RearBumperId" : -1', text)

def apply_unlock_air_sus(text):
    """✅ Working pattern: single regex matching whole object"""
    return re.sub(
        r'"AirSuspension"\s*:\s*\{[^}]*"Bought"\s*:\s*false[^}]*"Installed"\s*:\s*false[^}]*\}',
        '"AirSuspension" : {"Bought" : true, "Installed" : true}',
        text
    )

def apply_unlock_police(text):
    """✅ Working pattern: simple IsPolice flip"""
    return re.sub(r'"IsPolice"\s*:\s*false', '"IsPolice" : true', text)

def apply_unlock_bodykits(text):
    """Keep existing — array replacement"""
    lines = text.split("\n"); output = []; inside = False; current = ""
    arrs = [
        ["SpoilerIds", ",".join(str(i) for i in range(46))],
        ["FrontBumperIds", "0,1,2,3,4,5"], ["RearBumperIds", "0,1,2,3,4,5"],
        ["SkirtIds", "0,1,2,3,4,5"], ["HoodIds", "0,1,2,3,4"],
        ["HoodAirIntakeIds", ",".join(str(i) for i in range(46))],
        ["RoofAirIntakeIds", ",".join(str(i) for i in range(46))],
        ["FenderIds", "0,1,2,3,4,5"],
        ["TrimIds", ",".join(str(i) for i in range(46))],
    ]
    for line in lines:
        t = line.strip(); nl = line
        if inside:
            for a in arrs:
                if a[0] == current: nl = "        " + a[1]; break
            inside = False; output.append(nl); continue
        for a in arrs:
            if t.startswith(f'"{a[0]}"'): output.append(line); inside = True; current = a[0]; break
        if inside: continue
        output.append(nl)
    return "\n".join(output)

def ReplaceCarFields(text):
    """Full unlock - combines everything"""
    text = apply_unlock_air_sus(text)
    text = apply_unlock_police(text)
    lines = text.split("\n"); output = []; inside = False; current = ""
    arrs = [
        ["SpoilerIds", ",".join(str(i) for i in range(301))],
        ["FrontBumperIds", "0,1,2,3,4,5"], ["RearBumperIds", "0,1,2,3,4,5"],
        ["SkirtIds", "0,1,2,3,4,5"], ["HoodIds", "0,1,2,3,4"],
        ["HoodAirIntakeIds", ",".join(str(i) for i in range(301))],
        ["RoofAirIntakeIds", ",".join(str(i) for i in range(301))],
        ["FenderIds", "0,1,2,3,4,5"],
        ["TrimIds", ",".join(str(i) for i in range(301))],
    ]
    for line in lines:
        t = line.strip(); nl = line
        if inside:
            for a in arrs:
                if a[0] == current: nl = "        " + a[1]; break
            inside = False; output.append(nl); continue
        for a in arrs:
            if t.startswith(f'"{a[0]}"'): output.append(line); inside = True; current = a[0]; break
        if inside: continue
        if '"TopLight"' in t and ": -1" in line: nl = line.replace(": -1", ": 4")
        if '"Roobar"' in t and ": -1" in line: nl = line.replace(": -1", ": 2")
        if '"FrontInterior"' in t and ": -1" in line: nl = line.replace(": -1", ": 2")
        if '"RearInterior"' in t and ": -1" in line: nl = line.replace(": -1", ": 2")
        if '"Bought"' in t and ": false" in line: nl = line.replace(": false", ": true")
        if '"Installed"' in t and ": false" in line: nl = line.replace(": false", ": true")
        output.append(nl)
    return "\n".join(output)

# ============================================================
# LOGGING
# ============================================================
LOG_DIR = "ashlog"
def log_user(user_id):
    try:
        with open(USERS_FILE, "a") as f: f.write(f"{user_id}\n")
    except: pass

def log_user_action(user_id, email, cpm_type, code=""):
    try:
        try:
            with open(USERS_LOG, "r") as f: data = json.load(f)
        except: data = []
        data.append({"telegram_id": user_id, "email": email, "cpm_type": cpm_type,
                     "session_code": code, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        with open(USERS_LOG, "w") as f: json.dump(data, f, indent=4)
    except: pass

# ============================================================
# UI BUILDERS
# ============================================================
def back_button(callback="start_back"):
    return InlineKeyboardButton("🔙", callback_data=callback)

def get_mod_keyboard(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(T(uid, "full_unlock"), callback_data="UNLOCK_GIT")],
        [InlineKeyboardButton(T(uid, "individual"), callback_data="MENU_PARTS")],
        [InlineKeyboardButton(T(uid, "save_file"), callback_data="DOWNLOAD_ZIP")],
        [InlineKeyboardButton(T(uid, "main_menu"), callback_data="start_back")],
        [InlineKeyboardButton(T(uid, "exit_garage"), callback_data="CLEAR_ZIP")],
    ])

def get_parts_keyboard(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(T(uid, "air_sus"), callback_data="UNLOCK_AIR")],
        [InlineKeyboardButton(T(uid, "police"), callback_data="UNLOCK_POLICE")],
        [InlineKeyboardButton(T(uid, "bodykits"), callback_data="UNLOCK_BODYKITS")],
        [InlineKeyboardButton(T(uid, "mileage"), callback_data="MILEAGE_RESET")],
        [InlineKeyboardButton(T(uid, "front_bumper"), callback_data="REMOVE_FRONT")],
        [InlineKeyboardButton(T(uid, "rear_bumper"), callback_data="REMOVE_REAR")],
        [InlineKeyboardButton(T(uid, "back_garage"), callback_data="BACK_TO_GARAGE")],
    ])

def get_car_list_keyboard(cars, page, prefix):
    rows = []
    start = page * ITEMS_PER_PAGE; end = start + ITEMS_PER_PAGE
    total = len(cars) if isinstance(cars, list) else 0
    page_cars = cars[start:end] if isinstance(cars, list) else []
    print(f"[KB] page={page}, total={total}, showing={len(page_cars)}")
    for car in page_cars:
        if not isinstance(car, dict): continue
        try:
            v = car.get('vinyls', 0); w = car.get('window', 0)
            if v == -1 or v is None: v = 0
            if w == -1 or w is None: w = 0
            name = str(car.get('name') or f"Car {car.get('id', '?')}")[:25]
            idx = car.get('index', 0)
            rows.append([InlineKeyboardButton(f"🎨 {name} | V:{v} W:{w}", callback_data=f"{prefix}_sel_{idx}")])
        except Exception as e:
            print(f"[KB SKIP] {e}"); continue
    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️", callback_data=f"{prefix}_pg_{page-1}"))
    if end < total: nav.append(InlineKeyboardButton("➡️", callback_data=f"{prefix}_pg_{page+1}"))
    if nav: rows.append(nav)
    rows.append([InlineKeyboardButton("🔙", callback_data="start_back" if prefix == "src" else "cancel_api_transfer")])
    return InlineKeyboardMarkup(rows)

def get_lang_keyboard():
    rows = []
    for code, data in TRANSLATIONS.items():
        rows.append([InlineKeyboardButton(data["lang_name"], callback_data=f"LANG_{code}")])
    return InlineKeyboardMarkup(rows)

# ============================================================
# PRICES
# ============================================================
PRICES_TEXT = (
    "💎 <b>PRICING &amp; PLANS</b> 💎\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🚀 <b>CPM1 → CPM2 1-Click Transfer</b>\n"
    "<i>Or you can also do manually if you want.</i>\n\n"
    "✅ No ES3 required anymore!\n"
    "Just enter:\n"
    "• CPM1 Email + Password\n"
    "• CPM2 Email + Password\n\n"
    "After that, you'll get the full car list. Simply select the car whose design you want to transfer/change, and you're done!\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💳 <b>SUBSCRIPTIONS (Tokens + Time)</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "⭐ 1 Day + 100 Tokens — <b>100 Stars</b>\n"
    "⭐ 1 Week + 230 Tokens — <b>250 Stars</b>\n"
    "⭐ 2 Weeks + 350 Tokens — <b>325 Stars</b>\n"
    "⭐ 1 Month + 450 Tokens — <b>600 Stars</b>\n"
    "⭐ 3 Months + 650 Tokens — <b>800 Stars</b>\n\n"
    f"💵 1 Day + 200 Tokens — <b>$5</b> (₱{5 * USD_TO_PHP:.2f})\n"
    f"💵 1 Week + 450 Tokens — <b>$10</b> (₱{10 * USD_TO_PHP:.2f})\n"
    f"💵 2 Weeks + 650 Tokens — <b>$15</b> (₱{15 * USD_TO_PHP:.2f})\n"
    f"💵 1 Month + 850 Tokens — <b>$20</b> (₱{20 * USD_TO_PHP:.2f})\n"
    f"💵 3 Months + 950 Tokens — <b>$25</b> (₱{25 * USD_TO_PHP:.2f})\n"
    f"💵 Lifetime — <b>$45</b> (₱{45 * USD_TO_PHP:.2f})\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚙️ <b>FEATURE COSTS (Per Use)</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"🔐 CPM1/CPM2 Pass — <b>{COST_CPM_PASS} Tokens</b>\n"
    f"📀 Manual Conversion (CPM1→CPM2 / CPM2→CPM2) — <b>{COST_CONVERSION} Tokens</b>\n"
    f"🎨 API Vinyl Transfer (1-Click) — <b>{COST_VINYL_API} Tokens</b>\n"
    f"🔥 Unlocks (Full/Individual/Mileage/Bumper) — <b>{COST_UNLOCK} Tokens</b>\n"
    f"🚗 Coin Farm — <b>{COST_FARM} Tokens</b>\n\n"
    "⚠️ <i>Subscribed users do not get charged Tokens.</i>\n"
    "⚠️ <i>Lifetime users have unlimited access.</i>\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💳 <b>PAYMENT METHODS</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "• PayPal\n"
    "• PayMaya\n"
    "• GCash (To PayMaya via QR)\n\n"
    "👇 Dm: @Maakryan"
)

CONTACT_TEXT = (
    "📞 <b>CONTACT ADMIN</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "💬 <b>Telegram:</b> @Maakryan\n"
    "📱 <b>Facebook:</b> Markryan Manoguid\n"
    "🎵 <b>TikTok:</b> @zorolangg\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "📌 <i>MARK CPM1/2 CHANGER TOOL</i>"
)

async def prices_command(update, context):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("🔙", callback_data="start_back")]])
    await update.message.reply_text(PRICES_TEXT, parse_mode="HTML", reply_markup=kb)

async def contact_command(update, context):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="start_back")]])
    await update.message.reply_text(CONTACT_TEXT, parse_mode="HTML", reply_markup=kb)

async def language_command(update, context):
    uid = update.effective_user.id
    await update.message.reply_text(T(uid, "select_lang"), reply_markup=get_lang_keyboard())

# ============================================================
# START DASHBOARD
# ============================================================
async def start(update, context, keep_session=False):
    uid = update.effective_user.id
    un = update.effective_user.username or "NoUsername"
    if not keep_session: sessions.pop(uid, None)
    if hasattr(context, 'user_data'): context.user_data.clear()
    if hasattr(context, 'chat_data'): context.chat_data.clear()
    log_user(uid)

    # Language check first time
    langs = load_langs()
    if str(uid) not in langs and not update.callback_query:
        await update.message.reply_text(T(uid, "select_lang"), reply_markup=get_lang_keyboard())
        return WAIT_MENU

    coins = get_user_coins(uid); unl = is_unlimited(uid)
    stats = get_user_stats(uid)
    ops = stats.get("operations", 0); member_since = stats.get("member_since", "N/A")
    rank_name, rank_emoji, _ = get_user_rank(uid)

    coin_display = "∞" if unl else str(coins)
    wallet_status = T(uid, "unlimited") if unl else T(uid, "standard")

    if unl: sub_line = T(uid, "lifetime"); exp_line = T(uid, "never")
    elif is_subscribed(uid):
        data = load_coins(); exp = data.get(str(uid), {}).get("expiry") or "N/A"
        sub_line = T(uid, "active"); exp_line = exp
    else: sub_line = T(uid, "none"); exp_line = "—"

    caption = (
        "╔═══════════════════════════════╗\n"
        f"║  🎮  <b>MARK CPM TOOL</b>  🎮       ║\n"
        "║     <i>Premium Suite v2.0</i>      ║\n"
        "╚═══════════════════════════════╝\n\n"
        f"👤  {T(uid, 'account')}       :  @{un}\n"
        f"🆔  {T(uid, 'user_id')}       :  <code>{uid}</code>\n"
        f"🏆  Rank           :  {rank_emoji} {rank_name}\n\n"
        "┌───────────────────────────────┐\n"
        f"│  💎  <b>{T(uid, 'wallet')}</b>                    │\n"
        f"│  ├─ {T(uid, 'coins')}        :  <b>{coin_display}</b>\n"
        f"│  └─ {T(uid, 'status')}       :  {wallet_status}\n"
        "├───────────────────────────────┤\n"
        f"│  📅  <b>{T(uid, 'subscription')}</b>              │\n"
        f"│  ├─ {T(uid, 'plan')}         :  {sub_line}\n"
        f"│  └─ {T(uid, 'expires')}      :  {exp_line}\n"
        "├───────────────────────────────┤\n"
        f"│  📊  <b>{T(uid, 'statistics')}</b>                │\n"
        f"│  ├─ {T(uid, 'operations')}   :  <b>{ops}</b>\n"
        f"│  └─ {T(uid, 'member_since')} :  {member_since}\n"
        "└───────────────────────────────┘\n\n"
        f"⚡ <i>{T(uid, 'select_feature')}</i>"
    )

    kb = [
        [InlineKeyboardButton(f"━━━ ⚡ {T(uid, 'account_tools')} ━━━", callback_data="NOOP")],
        [InlineKeyboardButton(T(uid, "cpm1_pass"), callback_data="CPM1"),
         InlineKeyboardButton(T(uid, "cpm2_pass"), callback_data="CPM2")],
        [InlineKeyboardButton(f"━━━ 🔄 {T(uid, 'conversion')} ━━━", callback_data="NOOP")],
        [InlineKeyboardButton(T(uid, "cpm1_to_cpm2"), callback_data="C2C"),
         InlineKeyboardButton(T(uid, "cpm2_to_cpm2"), callback_data="C2C2")],
        [InlineKeyboardButton(f"━━━ 💎 {T(uid, 'premium')} ━━━", callback_data="NOOP")],
        [InlineKeyboardButton(T(uid, "api_vinyl"), callback_data="API_VINYL")],
        [InlineKeyboardButton(T(uid, "coin_farm"), callback_data="COIN_FARM"),
         InlineKeyboardButton(T(uid, "rank"), callback_data="SHOW_RANK")],
        [InlineKeyboardButton(f"━━━ 🛠️ {T(uid, 'garage')} ━━━", callback_data="NOOP")],
        [InlineKeyboardButton(T(uid, "unlock_all"), callback_data="UNLOCK_GIT"),
         InlineKeyboardButton(T(uid, "body_mods"), callback_data="LOCAL_MODS")],
        [InlineKeyboardButton(T(uid, "upload_zip"), callback_data="UPLOAD_ZIP")],
        [InlineKeyboardButton(f"━━━ 💰 {T(uid, 'info')} ━━━", callback_data="NOOP")],
        [InlineKeyboardButton(T(uid, "pricing"), callback_data="SHOW_PRICES"),
         InlineKeyboardButton(T(uid, "contact"), callback_data="SHOW_CONTACT")],
        [InlineKeyboardButton(T(uid, "language"), callback_data="SHOW_LANG")],
    ]

    if update.callback_query:
        q = update.callback_query
        try:
            await q.edit_message_caption(caption=caption, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            if "Message is not modified" in str(e): pass
            else:
                try:
                    await q.edit_message_text(text=caption, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
                except Exception as e2:
                    if "Message is not modified" in str(e2): pass
                    else:
                        await q.message.reply_photo(
                            photo="https://wallpapers-clan.com/wp-content/uploads/2024/11/sukuna-jujutsu-kaisen-evil-grin-wallpaper-preview.jpg",
                            caption=caption, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.message.reply_photo(
            photo="https://wallpapers-clan.com/wp-content/uploads/2024/11/sukuna-jujutsu-kaisen-evil-grin-wallpaper-preview.jpg",
            caption=caption, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
    return WAIT_MENU

# ============================================================
# API VINYL HANDLERS
# ============================================================
async def handle_api_cpm1_creds(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()
    if ":" not in text:
        await update.message.reply_text("❌ Format: `email:password`", parse_mode="Markdown",
                                         reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_API_CPM1_CREDS
    email, password = text.split(":", 1)
    email, password = email.strip(), password.strip()
    wait = await update.message.reply_text(T(uid, "connecting"))
    try:
        snap = await open_cpm1_cloud_session(email, password)
    except Exception as e:
        await wait.edit_text(f"❌ CPM1: {e}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        sessions.pop(uid, None); return ConversationHandler.END
    if snap.get("error"):
        await wait.edit_text(f"❌ CPM1: {snap['error']}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        sessions.pop(uid, None); return ConversationHandler.END
    cars = snap.get("cars") or []
    if not cars:
        await wait.edit_text("❌ No cars found.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        sessions.pop(uid, None); return ConversationHandler.END
    sessions[uid]["cpm1_email"] = email; sessions[uid]["cpm1_password"] = password
    sessions[uid]["cpm1_cars"] = cars; sessions[uid]["page"] = 0
    await wait.edit_text(f"✅ CPM1 {T(uid, 'connected')} {len(cars)} {T(uid, 'cars')}.")
    try:
        kb = get_car_list_keyboard(cars, 0, "src")
        await update.message.reply_text(T(uid, "select_src"), reply_markup=kb)
    except Exception as e:
        print(f"[CPM1 KB ERR] {e}")
        await update.message.reply_text(f"⚠️ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_MENU

async def handle_api_cpm2_creds(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()
    if ":" not in text:
        await update.message.reply_text("❌ Format: `email:password`", parse_mode="Markdown",
                                         reply_markup=InlineKeyboardMarkup([[back_button("cancel_api_transfer")]]))
        return WAIT_API_CPM2_CREDS
    email, password = text.split(":", 1)
    email, password = email.strip(), password.strip()
    wait = await update.message.reply_text(T(uid, "connecting"))
    try:
        snap = await open_cloud_vinyl_session(email, password)
    except Exception as e:
        await wait.edit_text(f"❌ CPM2: {e}", reply_markup=InlineKeyboardMarkup([[back_button("cancel_api_transfer")]]))
        sessions.pop(uid, None); return ConversationHandler.END
    if snap.get("error"):
        await wait.edit_text(f"❌ CPM2: {snap['error']}", reply_markup=InlineKeyboardMarkup([[back_button("cancel_api_transfer")]]))
        sessions.pop(uid, None); return ConversationHandler.END
    cars = snap.get("cars") or []
    if not cars:
        await wait.edit_text("❌ No cars found.", reply_markup=InlineKeyboardMarkup([[back_button("cancel_api_transfer")]]))
        sessions.pop(uid, None); return ConversationHandler.END
    sessions[uid]["cpm2_email"] = email; sessions[uid]["cpm2_password"] = password
    sessions[uid]["cpm2_cars"] = cars; sessions[uid]["page"] = 0
    await wait.edit_text(f"✅ CPM2 {T(uid, 'connected')} {len(cars)} {T(uid, 'cars')}.")
    try:
        kb = get_car_list_keyboard(cars, 0, "tgt")
        await update.message.reply_text(T(uid, "select_tgt"), reply_markup=kb)
    except Exception as e:
        print(f"[CPM2 KB ERR] {e}")
        await update.message.reply_text(f"⚠️ {e}", reply_markup=InlineKeyboardMarkup([[back_button("cancel_api_transfer")]]))
    return WAIT_MENU

# ============================================================
# COIN FARM HANDLERS
# ============================================================
async def handle_farm_email(update, context):
    uid = update.effective_user.id
    sessions[uid]["farm_email"] = update.message.text.strip()
    await update.message.reply_text(T(uid, "farm_pass"),
                                     reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_FARM_PASSWORD

async def handle_farm_password(update, context):
    uid = update.effective_user.id
    sessions[uid]["farm_password"] = update.message.text.strip()

    if not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
        if get_user_coins(uid) < COST_FARM:
            await update.message.reply_text(T(uid, "insufficient"),
                                             reply_markup=InlineKeyboardMarkup([[back_button()]]))
            sessions.pop(uid, None); return ConversationHandler.END
        deduct_coins(uid, COST_FARM)

    email = sessions[uid]["farm_email"]
    password = sessions[uid]["farm_password"]
    wait = await update.message.reply_text(T(uid, "farm_running"))

    try:
        token, uidl = await farm_login_async(email, password)
        if not token:
            await wait.edit_text("❌ Login failed.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
            sessions.pop(uid, None); return ConversationHandler.END
        initial = await farm_get_coins(token, uidl)
        await wait.edit_text(f"✅ Login OK!\n💰 {T(uid, 'farm_start')}: {initial:,}\n🔥 Farming...")
        success, ops, earned = await farm_coins(token, uidl)
        final = await farm_get_coins(token, uidl)
        await update.message.reply_text(
            f"{T(uid, 'farm_done')}\n"
            f"💰 {T(uid, 'farm_start')}: {initial:,}\n"
            f"🪙 {T(uid, 'farm_earned')}: {earned:,}\n"
            f"💎 {T(uid, 'farm_final')}: {final:,}\n"
            f"📊 {T(uid, 'farm_success')}: {success}/{ops}",
            reply_markup=InlineKeyboardMarkup([[back_button()]]))
        log_operation(uid)
    except Exception as e:
        await update.message.reply_text(f"❌ Farm error: {e}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    sessions.pop(uid, None)
    return WAIT_MENU

# ============================================================
# ES3 HANDLERS
# ============================================================
async def handle_cpm1_file(update, context):
    uid = update.effective_user.id
    doc = update.message.document
    if not doc:
        await update.message.reply_text("❌ Send CPM1 ES3 file.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_CPM1_FILE
    wait = await update.message.reply_text("⏳ Receiving CPM1...")
    try: fb = await (await doc.get_file()).download_as_bytearray()
    except Exception as e:
        await wait.edit_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]])); return WAIT_CPM1_FILE
    sessions[uid]["cpm1_file"] = fb
    sessions[uid]["cpm1_file_name_decoded"] = decode_es3_filename(doc.file_name)
    await wait.edit_text(T(uid, "sending_creds"), reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_CPM1_EMAIL

async def handle_cpm2_file(update, context):
    uid = update.effective_user.id
    doc = update.message.document
    if not doc:
        await update.message.reply_text("❌ Send CPM2 ES3 file.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_CPM2_FILE
    wait = await update.message.reply_text("⏳ Receiving CPM2...")
    try: fb = await (await doc.get_file()).download_as_bytearray()
    except Exception as e:
        await wait.edit_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]])); return WAIT_CPM2_FILE
    sessions[uid]["cpm2_file"] = fb
    sessions[uid]["cpm2_file_name_decoded"] = decode_es3_filename(doc.file_name)
    await wait.edit_text("📧 Send CPM2 email:", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_CPM2_EMAIL

async def handle_email_c2c(update, context):
    uid = update.effective_user.id
    if "cpm1_email" not in sessions.get(uid, {}):
        sessions[uid]["cpm1_email"] = update.message.text.strip()
        await update.message.reply_text("✅ CPM1 email. Send password:", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_CPM1_PASSWORD
    sessions[uid]["cpm2_email"] = update.message.text.strip()
    await update.message.reply_text("✅ CPM2 email. Send password:", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_CPM2_PASSWORD

async def handle_password_c2c(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()
    if "cpm1_pass" not in sessions[uid]:
        sessions[uid]["cpm1_pass"] = text
        await update.message.reply_text("✅ Upload CPM2 ES3:", reply_markup=InlineKeyboardMarkup([[back_button("start_back")]]))
        return WAIT_CPM2_FILE
    if "cpm2_pass" not in sessions[uid]: sessions[uid]["cpm2_pass"] = text
    if not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
        if get_user_coins(uid) < COST_CONVERSION:
            await update.message.reply_text(T(uid, "insufficient"), reply_markup=InlineKeyboardMarkup([[back_button()]]))
            return ConversationHandler.END
        deduct_coins(uid, COST_CONVERSION)
    c1f = sessions[uid]["cpm1_file"]; c1n = sessions[uid]["cpm1_file_name_decoded"]
    c1e = sessions[uid]["cpm1_email"]; c1p = sessions[uid]["cpm1_pass"]
    c2f = sessions[uid]["cpm2_file"]; c2n = sessions[uid]["cpm2_file_name_decoded"]
    c2e = sessions[uid]["cpm2_email"]; c2p = sessions[uid]["cpm2_pass"]
    code1 = generate_session_cpm1(c1n[:3], c1e, c1p)
    if code1.endswith("ERR"):
        await update.message.reply_text("❌ Invalid CPM1 creds.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return ConversationHandler.END
    code2 = generate_session_cpm2(c2n[:3], c2e, c2p)
    if code2.endswith("ERR"):
        await update.message.reply_text("❌ Invalid CPM2 creds.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return ConversationHandler.END
    try:
        dec = decrypt_es3(c1f, c1n[:3] + code1[3:])
        conv = encrypt_es3(dec, c2n[:3] + code2[3:])
    except Exception as e:
        await update.message.reply_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return ConversationHandler.END
    await update.message.reply_document(document=BytesIO(conv), filename=f"{c2n}.es3",
                                         caption="✅ CPM1→CPM2 complete!",
                                         reply_markup=InlineKeyboardMarkup([[back_button()]]))
    log_user_action(uid, f"{c1e}→{c2e}", "CPM1→CPM2"); log_operation(uid)
    sessions.pop(uid, None); return ConversationHandler.END

async def handle_cpm2a_file(update, context):
    uid = update.effective_user.id
    doc = update.message.document
    if not doc:
        await update.message.reply_text("❌ Send source ES3.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_CPM2A_FILE
    wait = await update.message.reply_text("⏳ Receiving...")
    try: fb = await (await doc.get_file()).download_as_bytearray()
    except Exception as e:
        await wait.edit_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]])); return WAIT_CPM2A_FILE
    sessions[uid]["cpm2a_file"] = fb
    sessions[uid]["cpm2a_file_name"] = decode_es3_filename(doc.file_name)
    await wait.edit_text("📧 Source email:", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_CPM2A_EMAIL

async def handle_cpm2a_email(update, context):
    sessions[update.effective_user.id]["cpm2a_email"] = update.message.text.strip()
    await update.message.reply_text("🔑 Source password:", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_CPM2A_PASSWORD

async def handle_cpm2a_password(update, context):
    sessions[update.effective_user.id]["cpm2a_pass"] = update.message.text.strip()
    await update.message.reply_text("📦 Upload target ES3:", reply_markup=InlineKeyboardMarkup([[back_button("start_back")]]))
    return WAIT_CPM2B_FILE

async def handle_cpm2b_file(update, context):
    uid = update.effective_user.id
    doc = update.message.document
    if not doc:
        await update.message.reply_text("❌ Send target ES3.", reply_markup=InlineKeyboardMarkup([[back_button("start_back")]]))
        return WAIT_CPM2B_FILE
    wait = await update.message.reply_text("⏳ Receiving...")
    try: fb = await (await doc.get_file()).download_as_bytearray()
    except Exception as e:
        await wait.edit_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button("start_back")]])); return WAIT_CPM2B_FILE
    sessions[uid]["cpm2b_file"] = fb
    sessions[uid]["cpm2b_file_name"] = decode_es3_filename(doc.file_name)
    await wait.edit_text("📧 Target email:", reply_markup=InlineKeyboardMarkup([[back_button("start_back")]]))
    return WAIT_CPM2B_EMAIL

async def handle_cpm2b_email(update, context):
    sessions[update.effective_user.id]["cpm2b_email"] = update.message.text.strip()
    await update.message.reply_text("🔑 Target password:", reply_markup=InlineKeyboardMarkup([[back_button("start_back")]]))
    return WAIT_CPM2B_PASSWORD

async def handle_cpm2b_password(update, context):
    uid = update.effective_user.id
    sessions[uid]["cpm2b_pass"] = update.message.text.strip()
    if not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
        if get_user_coins(uid) < COST_CONVERSION:
            await update.message.reply_text(T(uid, "insufficient"), reply_markup=InlineKeyboardMarkup([[back_button()]]))
            return ConversationHandler.END
        deduct_coins(uid, COST_CONVERSION)
    sf = sessions[uid]["cpm2a_file"]; sn = sessions[uid]["cpm2a_file_name"]
    se = sessions[uid]["cpm2a_email"]; sp = sessions[uid]["cpm2a_pass"]
    tf = sessions[uid]["cpm2b_file"]; tn = sessions[uid]["cpm2b_file_name"]
    te = sessions[uid]["cpm2b_email"]; tp = sessions[uid]["cpm2b_pass"]
    cs = generate_session_cpm2(sn[:3], se, sp); ct = generate_session_cpm2(tn[:3], te, tp)
    if cs.endswith("ERR") or ct.endswith("ERR"):
        await update.message.reply_text("❌ Invalid creds.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return ConversationHandler.END
    try:
        dec = decrypt_es3(sf, sn[:3] + cs[3:])
        conv = encrypt_es3(dec, tn[:3] + ct[3:])
    except Exception as e:
        await update.message.reply_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return ConversationHandler.END
    await update.message.reply_document(document=BytesIO(conv), filename=f"{tn}.es3",
                                         caption="✅ CPM2→CPM2 complete!",
                                         reply_markup=InlineKeyboardMarkup([[back_button()]]))
    log_user_action(uid, f"{se}→{te}", "CPM2→CPM2"); log_operation(uid)
    sessions.pop(uid, None); return ConversationHandler.END

async def handle_file(update, context):
    uid = update.effective_user.id
    doc = update.message.document
    if not doc:
        await update.message.reply_text("❌ Send ES3.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_FILE
    filename = doc.file_name or "ES3_FILE"
    decoded = decode_es3_filename(filename)
    sessions[uid]["es3_first3"] = decoded[:3]
    log_user(uid)
    await update.message.reply_text("✅ ES3 received. Send email:", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_EMAIL

async def handle_email(update, context):
    uid = update.effective_user.id
    if uid not in sessions or "es3_first3" not in sessions[uid]:
        await update.message.reply_text("❌ Send ES3 first.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_FILE
    sessions[uid]["email"] = update.message.text.strip()
    await update.message.reply_text("✅ Send password:", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_PASSWORD

async def handle_password(update, context):
    uid = update.effective_user.id
    if uid not in sessions or "email" not in sessions[uid]:
        await update.message.reply_text("❌ Send ES3 + email.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_FILE
    pw = update.message.text.strip()
    choice = sessions[uid]["choice"]; es3 = sessions[uid]["es3_first3"]; em = sessions[uid]["email"]
    if not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
        if get_user_coins(uid) < COST_CPM_PASS:
            await update.message.reply_text(T(uid, "insufficient"), reply_markup=InlineKeyboardMarkup([[back_button()]]))
            return ConversationHandler.END
        deduct_coins(uid, COST_CPM_PASS)
    wait = await update.message.reply_text("🔐 Logging in...")
    code = generate_session_cpm1(es3, em, pw) if choice == "CPM1" else generate_session_cpm2(es3, em, pw)
    if code.endswith("ERR"):
        await wait.edit_text("❌ Login failed.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        sessions.pop(uid, None); return ConversationHandler.END
    await wait.edit_text(f"✅ Code: `{code}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    log_user_action(uid, em, choice, code); log_operation(uid)
    sessions.pop(uid, None); return ConversationHandler.END

async def handle_zip(update, context):
    uid = update.effective_user.id
    doc = update.message.document
    if not doc or not doc.file_name.endswith(".zip"):
        await update.message.reply_text("❌ Send .zip file.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return WAIT_ZIP
    wait = await update.message.reply_text("⏳ Downloading...")
    try:
        temp_zip = tempfile.mktemp(suffix=".zip")
        await (await doc.get_file()).download_to_drive(temp_zip)
    except Exception as e:
        await wait.edit_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]])); return WAIT_ZIP
    await wait.edit_text("⏳ Extracting...")
    try:
        extract_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(temp_zip, 'r') as zr: zr.extractall(extract_dir)
        extract_dir = get_actual_es3_folder(extract_dir); os.remove(temp_zip)
    except Exception as e:
        await wait.edit_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]])); return WAIT_ZIP
    if uid not in sessions: sessions[uid] = {}
    sessions[uid]["es3_folder"] = extract_dir
    files = [f for f in os.listdir(extract_dir) if os.path.isfile(os.path.join(extract_dir, f))]
    key_set = False
    for f in files:
        try:
            dec = decode_es3_filename(f)
            if len(dec) >= 3: sessions[uid]["es3_folder_key"] = dec[:3]; key_set = True; break
        except: continue
    if not key_set:
        await wait.edit_text("❌ No ES3 key.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        return ConversationHandler.END
    await wait.edit_text(f"✅ ZIP loaded ({len(files)}). Select mod:", reply_markup=get_mod_keyboard(uid))
    return WAIT_MENU

async def send_modified_zip(msg, uid):
    folder = sessions[uid].get("es3_folder")
    if not folder:
        await msg.reply_text("❌ No folder.", reply_markup=InlineKeyboardMarkup([[back_button()]])); return
    out = tempfile.mktemp(suffix="_modified.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder):
            for f in files:
                fp = os.path.join(root, f); arc = os.path.relpath(fp, folder)
                z.write(fp, arc)
    with open(out, "rb") as f:
        await msg.reply_document(document=f, filename="es3_modified.zip",
                                  caption="✅ Modified ZIP!",
                                  reply_markup=get_mod_keyboard(uid))
    os.remove(out)

async def apply_unlock_all_git(update, context):
    uid = update.effective_user.id
    msg = update.callback_query.message
    if uid not in saved_cpm2_accounts:
        await msg.reply_text("❌ Login CPM2 first.", reply_markup=InlineKeyboardMarkup([[back_button()]])); return
    folder = sessions[uid].get("es3_folder")
    if not folder:
        await msg.reply_text("❌ No ZIP.", reply_markup=InlineKeyboardMarkup([[back_button()]])); return
    try:
        r = requests.get("https://raw.githubusercontent.com/ash28don/rish-setup/main/UnlockAll.txt", timeout=25)
        data = r.content
        lid = saved_cpm2_accounts[uid]["localId"]
        key = sessions[uid].get("es3_folder_key", "XXX")
        sp = build_es3_password(key[:3], lid)
        for f in os.listdir(folder):
            path = os.path.join(folder, f); dec = decode_es3_filename(f)
            if "39dPlayerData" in dec or "PlayerData" in dec:
                with open(path, "wb") as o: o.write(encrypt_es3(data, sp))
                await msg.reply_text("🔥 Unlock ALL!")
                log_operation(uid); await send_modified_zip(msg, uid); return
        await msg.reply_text("❌ PlayerData not found.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    except Exception as e:
        await msg.reply_text(f"❌ {e}", reply_markup=InlineKeyboardMarkup([[back_button()]]))

async def apply_individual_mod(update, context, mod_type):
    q = update.callback_query; msg = q.message if q else update.message
    uid = update.effective_user.id
    if uid not in saved_cpm2_accounts:
        await msg.reply_text("❌ Login CPM2 first.", reply_markup=InlineKeyboardMarkup([[back_button()]])); return
    folder = sessions[uid].get("es3_folder")
    if not folder:
        await msg.reply_text("❌ No ZIP.", reply_markup=InlineKeyboardMarkup([[back_button()]])); return
    lid = saved_cpm2_accounts[uid]["localId"]
    sp = build_es3_password(sessions[uid]["es3_folder_key"][:3], lid)
    files = os.listdir(folder); proc = mod = fail = 0
    names = {"air": "Air Suspension", "police": "Police", "bodykits": "Bodykits",
             "mileage": "Mileage Reset", "front": "Front Bumper Remove", "rear": "Rear Bumper Remove"}
    await msg.reply_text(T(uid, "applying", mod=names[mod_type]))
    for f in files:
        path = os.path.join(folder, f)
        if not os.path.isfile(path): continue
        dec = decode_es3_filename(f)
        if "maindata" not in dec.lower(): continue
        try:
            enc = open(path, "rb").read()
            decrypted = decrypt_es3(enc, sp)
            try: text = decrypted.decode("utf-8")
            except: text = decrypted.decode("utf-8", errors="ignore")
            if mod_type == "air": new = apply_unlock_air_sus(text)
            elif mod_type == "police": new = apply_unlock_police(text)
            elif mod_type == "bodykits": new = apply_unlock_bodykits(text)
            elif mod_type == "mileage": new = apply_mileage_reset(text)
            elif mod_type == "front": new = apply_remove_front_bumper(text)
            elif mod_type == "rear": new = apply_remove_rear_bumper(text)
            else: new = text
            if new == text: proc += 1; continue
            with open(path, "wb") as o: o.write(encrypt_es3(new.encode("utf-8"), sp))
            mod += 1; proc += 1
        except Exception as e:
            print(f"[{mod_type}] {f} | {e}"); fail += 1
    await msg.reply_text(
        f"✅ {names[mod_type]}\n📂 {T(uid, 'total')}: {len(files)}\n"
        f"⚙️ {T(uid, 'processed')}: {proc}\n✅ {T(uid, 'modified')}: {mod}\n❌ {T(uid, 'failed')}: {fail}",
        reply_markup=InlineKeyboardMarkup([[back_button()]]))
    log_operation(uid); await send_modified_zip(msg, uid)

async def apply_local_mods(update, context):
    q = update.callback_query; msg = q.message if q else update.message
    uid = update.effective_user.id
    if uid not in saved_cpm2_accounts:
        await msg.reply_text("❌ Login CPM2 first.", reply_markup=InlineKeyboardMarkup([[back_button()]])); return
    folder = sessions[uid].get("es3_folder")
    if not folder:
        await msg.reply_text("❌ No ZIP.", reply_markup=InlineKeyboardMarkup([[back_button()]])); return
    lid = saved_cpm2_accounts[uid]["localId"]
    sp = build_es3_password(sessions[uid]["es3_folder_key"][:3], lid)
    files = os.listdir(folder); proc = mod = fail = 0
    await msg.reply_text("🚗 Applying Full Mods...")
    for f in files:
        path = os.path.join(folder, f)
        if not os.path.isfile(path): continue
        dec = decode_es3_filename(f)
        if "maindata" not in dec.lower(): continue
        try:
            enc = open(path, "rb").read()
            decrypted = decrypt_es3(enc, sp)
            try: text = decrypted.decode("utf-8")
            except: text = decrypted.decode("utf-8", errors="ignore")
            new = ReplaceCarFields(text)
            if new == text: proc += 1; continue
            with open(path, "wb") as o: o.write(encrypt_es3(new.encode("utf-8"), sp))
            mod += 1; proc += 1
        except: fail += 1
    await msg.reply_text(f"✅ Done\n📂 {len(files)} | ⚙️ {proc} | ✅ {mod} | ❌ {fail}",
                          reply_markup=InlineKeyboardMarkup([[back_button()]]))
    log_operation(uid); await send_modified_zip(msg, uid)

async def cancel(update, context):
    uid = update.effective_user.id
    if uid in sessions: sessions.pop(uid)
    await update.message.reply_text("❌ Cancelled.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return ConversationHandler.END

async def safe_edit(query, text, reply_markup=None):
    kw = {"parse_mode": "HTML"}
    if reply_markup: kw["reply_markup"] = reply_markup
    try: await query.edit_message_caption(caption=text, **kw)
    except:
        try: await query.edit_message_text(text=text, **kw)
        except: await query.message.reply_text(text, **kw)

# ============================================================
# MENU CHOICE
# ============================================================
async def menu_choice(update, context):
    q = update.callback_query; await q.answer()
    choice = q.data; uid = q.from_user.id
    log_user(uid)
    if uid not in sessions: sessions[uid] = {}

    if choice == "NOOP": return WAIT_MENU
    if choice == "start_back":
        await start(update, context, keep_session=True); return WAIT_MENU
    if choice == "BACK_TO_GARAGE":
        await safe_edit(q, "🛠️", get_mod_keyboard(uid)); return WAIT_MENU
    if choice == "SHOW_LANG":
        await q.message.reply_text(T(uid, "select_lang"), reply_markup=get_lang_keyboard()); return WAIT_MENU
    if choice.startswith("LANG_"):
        lang = choice.replace("LANG_", "")
        if lang in TRANSLATIONS:
            set_user_lang(uid, lang)
            await q.message.reply_text(T(uid, "lang_saved"))
        await start(update, context, keep_session=True)
        return WAIT_MENU
    if choice == "SHOW_PRICES":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}")],
                                     [InlineKeyboardButton("🔙", callback_data="start_back")]])
        await q.message.reply_text(PRICES_TEXT, parse_mode="HTML", reply_markup=kb); return WAIT_MENU
    if choice == "SHOW_CONTACT":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="start_back")]])
        await q.message.reply_text(CONTACT_TEXT, parse_mode="HTML", reply_markup=kb); return WAIT_MENU
    if choice == "SHOW_RANK":
        stats = get_user_stats(uid); rank_name, rank_emoji, daily = get_user_rank(uid)
        text = (f"{T(uid, 'rank_title')}\n\n"
                f"{rank_emoji} {T(uid, 'your_rank')}: {rank_name}\n"
                f"📊 {T(uid, 'operations')}: {stats.get('operations', 0)}\n"
                f"📅 Daily: {stats.get('daily', 0)}/{daily}\n\n"
                f"{T(uid, 'rank_list')}")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="start_back")]])
        await q.message.reply_text(text, reply_markup=kb); return WAIT_MENU
    if choice == "cancel_api_transfer":
        sessions.pop(uid, None); await start(update, context); return WAIT_MENU

    if choice.startswith("src_pg_"):
        try:
            page = int(choice.split("_")[2])
            cars = sessions[uid].get("cpm1_cars", [])
            sessions[uid]["page"] = page
            await safe_edit(q, T(uid, "select_src"), get_car_list_keyboard(cars, page, "src"))
        except Exception as e: print(f"[SRC PG] {e}")
        return WAIT_MENU
    if choice.startswith("tgt_pg_"):
        try:
            page = int(choice.split("_")[2])
            cars = sessions[uid].get("cpm2_cars", [])
            sessions[uid]["page"] = page
            await safe_edit(q, T(uid, "select_tgt"), get_car_list_keyboard(cars, page, "tgt"))
        except Exception as e: print(f"[TGT PG] {e}")
        return WAIT_MENU

    if choice.startswith("src_sel_"):
        try:
            idx = int(choice.split("_")[2])
            cars = sessions[uid].get("cpm1_cars", [])
            car = next((c for c in cars if c.get("index") == idx), None)
            if not car:
                await safe_edit(q, "❌ Car not found."); return WAIT_MENU
            sessions[uid]["donor_car"] = car; sessions[uid]["donor_index"] = idx
            await q.message.reply_text(
                f"✅ {T(uid, 'source')}: {car['name']}\n\n{T(uid, 'send_creds')}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[back_button("cancel_api_transfer")]]))
            return WAIT_API_CPM2_CREDS
        except Exception as e:
            print(f"[SRC SEL] {e}"); sessions.pop(uid, None); return WAIT_MENU

    if choice.startswith("tgt_sel_"):
        try:
            idx = int(choice.split("_")[2])
            donor = sessions[uid].get("donor_car")
            if not donor:
                await safe_edit(q, "❌ No source."); return WAIT_MENU
            if not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
                if get_user_coins(uid) < COST_VINYL_API:
                    await safe_edit(q, T(uid, "need_coins", amount=COST_VINYL_API, have=get_user_coins(uid)))
                    return WAIT_MENU
                deduct_coins(uid, COST_VINYL_API)
            await safe_edit(q, "⏳ API Transfer...")
            result = await execute_api_vinyl_transfer(
                sessions[uid]["cpm1_email"], sessions[uid]["cpm1_password"],
                sessions[uid]["cpm2_email"], sessions[uid]["cpm2_password"],
                sessions[uid]["donor_index"], idx)
            kb = InlineKeyboardMarkup([[back_button()]])
            if result.get("error"):
                await q.message.reply_text(f"❌ {T(uid, 'transfer_failed')}: {result['error']}", reply_markup=kb)
            else:
                tgt_cars = sessions[uid].get("cpm2_cars", [])
                tgt = next((c for c in tgt_cars if c.get("index") == idx), None)
                await q.message.reply_text(
                    f"✅ {T(uid, 'transfer_complete')}\n\n"
                    f"🎨 {T(uid, 'source')}: {donor['name']}\n"
                    f"🎯 {T(uid, 'target')}: {tgt['name'] if tgt else idx}\n\n"
                    f"💎 Sent: {result['sent']} | Verified: {result['verified']}", reply_markup=kb)
                log_operation(uid)
            sessions.pop(uid, None); return WAIT_MENU
        except Exception as e:
            print(f"[TGT SEL] {e}"); sessions.pop(uid, None); return WAIT_MENU

    if choice in ["CPM1", "CPM2"] and get_user_coins(uid) < COST_CPM_PASS and not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
        await safe_edit(q, T(uid, "insufficient"), InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU
    if choice in ["C2C", "C2C2"] and get_user_coins(uid) < COST_CONVERSION and not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
        await safe_edit(q, T(uid, "insufficient"), InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU
    if choice == "API_VINYL" and get_user_coins(uid) < COST_VINYL_API and not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
        await safe_edit(q, T(uid, "insufficient"), InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU

    sessions[uid]["choice"] = choice

    if choice == "CPM1":
        await safe_edit(q, "✅ CPM1. Upload ES3:", InlineKeyboardMarkup([[back_button()]])); return WAIT_FILE
    elif choice == "CPM2":
        await safe_edit(q, "✅ CPM2. Upload ES3:", InlineKeyboardMarkup([[back_button()]])); return WAIT_FILE
    elif choice == "C2C":
        await safe_edit(q, "✅ CPM1→CPM2. Upload CPM1 ES3:", InlineKeyboardMarkup([[back_button()]])); return WAIT_CPM1_FILE
    elif choice == "C2C2":
        await safe_edit(q, "✅ CPM2→CPM2. Upload source ES3:", InlineKeyboardMarkup([[back_button()]])); return WAIT_CPM2A_FILE
    elif choice == "API_VINYL":
        await safe_edit(q, f"🎨 <b>API Vinyl Transfer</b>\n\n{T(uid, 'send_creds')}",
                         InlineKeyboardMarkup([[back_button()]]))
        return WAIT_API_CPM1_CREDS
    elif choice == "COIN_FARM":
        await safe_edit(q, T(uid, "farm_prompt"), InlineKeyboardMarkup([[back_button()]]))
        return WAIT_FARM_EMAIL
    elif choice == "ACCOUNT":
        kb = [[InlineKeyboardButton("🔐 CPM2 Login", callback_data="LOGINCPM2")],
              [InlineKeyboardButton("✉️ Email", callback_data="CHANGEEMAIL")],
              [InlineKeyboardButton("🔑 Password", callback_data="CHANGEPASS")],
              [InlineKeyboardButton("🔙", callback_data="start_back")]]
        await safe_edit(q, "⚙️ Account Manager", InlineKeyboardMarkup(kb)); return WAIT_MENU
    elif choice == "UPLOAD_ZIP":
        await safe_edit(q, T(uid, "upload_es3"), InlineKeyboardMarkup([[back_button()]])); return WAIT_ZIP
    elif choice == "MENU_PARTS":
        await safe_edit(q, T(uid, "individual"), get_parts_keyboard(uid)); return WAIT_MENU
    elif choice in ["UNLOCK_GIT", "LOCAL_MODS", "UNLOCK_AIR", "UNLOCK_POLICE", "UNLOCK_BODYKITS",
                     "MILEAGE_RESET", "REMOVE_FRONT", "REMOVE_REAR"]:
        if uid not in saved_cpm2_accounts:
            sessions[uid]["pending_mod"] = choice
            await safe_edit(q, "🔐 Login CPM2 first. Send email:", InlineKeyboardMarkup([[back_button()]]))
            return WAIT_LOGIN_EMAIL
        if not sessions[uid].get("es3_folder"):
            await safe_edit(q, "❌ Upload ZIP first.", InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU
        if not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
            if get_user_coins(uid) < COST_UNLOCK:
                await safe_edit(q, T(uid, "insufficient"), InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU
            deduct_coins(uid, COST_UNLOCK)
        if choice == "UNLOCK_GIT":
            await safe_edit(q, "⬇️ Unlock ALL..."); await apply_unlock_all_git(update, context)
        elif choice == "LOCAL_MODS":
            await safe_edit(q, "🚗 Full Mods..."); await apply_local_mods(update, context)
        elif choice == "UNLOCK_AIR":
            await safe_edit(q, "🚗 Air Sus..."); await apply_individual_mod(update, context, "air")
        elif choice == "UNLOCK_POLICE":
            await safe_edit(q, "🚓 Police..."); await apply_individual_mod(update, context, "police")
        elif choice == "UNLOCK_BODYKITS":
            await safe_edit(q, "🎨 Bodykits..."); await apply_individual_mod(update, context, "bodykits")
        elif choice == "MILEAGE_RESET":
            await safe_edit(q, "📉 Mileage..."); await apply_individual_mod(update, context, "mileage")
        elif choice == "REMOVE_FRONT":
            await safe_edit(q, "🔧 Front Bumper..."); await apply_individual_mod(update, context, "front")
        elif choice == "REMOVE_REAR":
            await safe_edit(q, "🔧 Rear Bumper..."); await apply_individual_mod(update, context, "rear")
        return WAIT_MENU
    elif choice == "DOWNLOAD_ZIP":
        folder = sessions[uid].get("es3_folder")
        if not folder:
            await q.message.reply_text("❌ No ZIP.", reply_markup=InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU
        await send_modified_zip(q.message, uid); return WAIT_MENU
    elif choice == "CLEAR_ZIP":
        sessions.pop(uid, None); await start(update, context); return WAIT_MENU
    elif choice == "LOGINCPM2":
        await safe_edit(q, "📧 Send CPM2 email:", InlineKeyboardMarkup([[back_button()]])); return WAIT_LOGIN_EMAIL
    elif choice == "CHANGEEMAIL":
        if uid not in saved_cpm2_accounts:
            await safe_edit(q, "❌ Login first.", InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU
        await safe_edit(q, "📧 New email:", InlineKeyboardMarkup([[back_button()]])); return WAIT_NEW_EMAIL
    elif choice == "CHANGEPASS":
        if uid not in saved_cpm2_accounts:
            await safe_edit(q, "❌ Login first.", InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU
        await safe_edit(q, "🔑 New password:", InlineKeyboardMarkup([[back_button()]])); return WAIT_NEW_PASSWORD
    else:
        await safe_edit(q, "❓", InlineKeyboardMarkup([[back_button()]])); return WAIT_MENU

# ============================================================
# ACCOUNT MANAGER
# ============================================================
async def handle_login_email(update, context):
    sessions[update.effective_user.id]["login_email"] = update.message.text.strip()
    await update.message.reply_text("🔑 CPM2 password:", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return WAIT_LOGIN_PASSWORD

async def handle_login_password(update, context):
    uid = update.effective_user.id
    pw = update.message.text.strip(); em = sessions[uid]["login_email"]
    resp = login_request(em, pw, CPM2_API_KEY)
    if "idToken" not in resp:
        await update.message.reply_text("❌ Login failed.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
        sessions[uid].pop("pending_mod", None); return ConversationHandler.END
    saved_cpm2_accounts[uid] = {"idToken": resp["idToken"], "localId": resp["localId"], "email": em}
    await update.message.reply_text("✅ CPM2 linked!", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    pm = sessions[uid].pop("pending_mod", None)
    if pm:
        if not sessions[uid].get("es3_folder"):
            await update.message.reply_text("✅ Upload ZIP.", reply_markup=InlineKeyboardMarkup([[back_button()]]))
            return WAIT_ZIP
        if not is_unlimited(uid) and uid not in ADMIN_ID and not is_subscribed(uid):
            if get_user_coins(uid) < COST_UNLOCK:
                await update.message.reply_text(T(uid, "insufficient"), reply_markup=InlineKeyboardMarkup([[back_button()]]))
                return ConversationHandler.END
            deduct_coins(uid, COST_UNLOCK)
        if pm == "UNLOCK_GIT": await apply_unlock_all_git(update, context)
        elif pm == "LOCAL_MODS": await apply_local_mods(update, context)
        elif pm == "UNLOCK_AIR": await apply_individual_mod(update, context, "air")
        elif pm == "UNLOCK_POLICE": await apply_individual_mod(update, context, "police")
        elif pm == "UNLOCK_BODYKITS": await apply_individual_mod(update, context, "bodykits")
        elif pm == "MILEAGE_RESET": await apply_individual_mod(update, context, "mileage")
        elif pm == "REMOVE_FRONT": await apply_individual_mod(update, context, "front")
        elif pm == "REMOVE_REAR": await apply_individual_mod(update, context, "rear")
        return WAIT_MENU
    return ConversationHandler.END

async def handle_new_email(update, context):
    uid = update.effective_user.id; ne = update.message.text.strip()
    acc = saved_cpm2_accounts[uid]
    resp = update_request(acc["idToken"], CPM2_API_KEY, new_email=ne)
    if "email" in resp:
        acc["email"] = resp["email"]
        if "idToken" in resp: acc["idToken"] = resp["idToken"]
        await update.message.reply_text(f"✅ Email: {resp['email']}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    else:
        await update.message.reply_text(f"❌ {resp}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return ConversationHandler.END

async def handle_new_password(update, context):
    uid = update.effective_user.id; np = update.message.text.strip()
    acc = saved_cpm2_accounts[uid]
    resp = update_request(acc["idToken"], CPM2_API_KEY, new_password=np)
    if "idToken" in resp:
        acc["idToken"] = resp["idToken"]
        await update.message.reply_text("✅ Password changed!", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    else:
        await update.message.reply_text(f"❌ {resp}", reply_markup=InlineKeyboardMarkup([[back_button()]]))
    return ConversationHandler.END

# ============================================================
# ADMIN
# ============================================================
async def addcoins_command(update, context):
    if update.effective_user.id not in ADMIN_ID: await update.message.reply_text("❌"); return
    try:
        add_coins(int(context.args[0]), int(context.args[1]))
        await update.message.reply_text(f"✅ +{context.args[1]} coins to {context.args[0]}.")
    except: await update.message.reply_text("/addcoins <user_id> <amount>")

async def set_coins_command(update, context):
    if update.effective_user.id not in ADMIN_ID: await update.message.reply_text("❌"); return
    try:
        set_coins(int(context.args[0]), int(context.args[1]))
        await update.message.reply_text(f"✅ Set {context.args[1]} for {context.args[0]}.")
    except: await update.message.reply_text("/setcoins <user_id> <amount>")

async def unlimited_command(update, context):
    if update.effective_user.id not in ADMIN_ID: await update.message.reply_text("❌"); return
    try:
        set_unlimited(int(context.args[0]), context.args[1].lower() in ["true", "1", "yes"])
        await update.message.reply_text(f"✅ Unlimited {context.args[0]}.")
    except: await update.message.reply_text("/unlimited <user_id> <True/False>")

async def balance_command(update, context):
    uid = update.effective_user.id
    try:
        tid = int(context.args[0]) if context.args else uid
        await update.message.reply_text(f"💰 User {tid}: {get_user_coins(tid)}{' (Unlimited)' if is_unlimited(tid) else ''}.")
    except: await update.message.reply_text("/balance [user_id]")

async def stopbot_command(update, context):
    if update.effective_user.id not in ADMIN_ID: await update.message.reply_text("❌"); return
    await update.message.reply_text("🛑"); sys.exit(0)

async def subscribe_command(update, context):
    if update.effective_user.id not in ADMIN_ID: await update.message.reply_text("❌"); return
    args = context.args
    if not args or len(args) < 2: await update.message.reply_text("/subscribe <user_id> <amount> [days/weeks/months]"); return
    try:
        tid = int(args[0]); amt = int(args[1])
        unit = args[2].lower() if len(args) >= 3 else "months"
        if amt <= 0:
            set_subscribed(tid, False, 0); await update.message.reply_text(f"❌ Removed for {tid}."); return
        if unit in ["day", "days", "d"]: days = amt; label = f"{amt}d"
        elif unit in ["week", "weeks", "w"]: days = amt * 7; label = f"{amt}w"
        elif unit in ["month", "months", "m"]: days = amt * 30; label = f"{amt}mo"
        else: await update.message.reply_text("❌ Invalid unit."); return
        set_subscribed(tid, True, days)
        exp = datetime.date.today() + datetime.timedelta(days=days)
        await update.message.reply_text(f"✅ {tid} for {label}. Expires {exp}")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def error_handler(update, context):
    print("Exception:", context.error)

async def post_init(app):
    try:
        await app.bot.set_my_commands([
            BotCommand("start", "🚀 Start"),
            BotCommand("prices", "💎 Prices"),
            BotCommand("language", "🌐 Language"),
            BotCommand("balance", "💰 Balance"),
            BotCommand("cancel", "❌ Cancel"),
        ])
        print("✅ Commands registered.")
    except Exception as e: print(f"⚠️ {e}")

# ============================================================
# MAIN
# ============================================================
def main():
    request = HTTPXRequest(connection_pool_size=20, connect_timeout=60.0,
                           read_timeout=60.0, write_timeout=60.0, pool_timeout=60.0)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).post_init(post_init).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("prices", prices_command),
            CommandHandler("contact", contact_command),
            CommandHandler("language", language_command),
        ],
        states={
            WAIT_MENU: [CallbackQueryHandler(menu_choice)],
            WAIT_FILE: [MessageHandler(filters.Document.ALL, handle_file), CallbackQueryHandler(menu_choice)],
            WAIT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email), CallbackQueryHandler(menu_choice)],
            WAIT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password), CallbackQueryHandler(menu_choice)],
            WAIT_LOGIN_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_login_email), CallbackQueryHandler(menu_choice)],
            WAIT_LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_login_password), CallbackQueryHandler(menu_choice)],
            WAIT_NEW_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_email), CallbackQueryHandler(menu_choice)],
            WAIT_NEW_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_password), CallbackQueryHandler(menu_choice)],
            WAIT_CPM1_FILE: [MessageHandler(filters.Document.ALL, handle_cpm1_file), CallbackQueryHandler(menu_choice)],
            WAIT_CPM1_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email_c2c), CallbackQueryHandler(menu_choice)],
            WAIT_CPM1_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password_c2c), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2_FILE: [MessageHandler(filters.Document.ALL, handle_cpm2_file), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email_c2c), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password_c2c), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2A_FILE: [MessageHandler(filters.Document.ALL, handle_cpm2a_file), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2A_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cpm2a_email), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2A_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cpm2a_password), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2B_FILE: [MessageHandler(filters.Document.ALL, handle_cpm2b_file), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2B_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cpm2b_email), CallbackQueryHandler(menu_choice)],
            WAIT_CPM2B_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cpm2b_password), CallbackQueryHandler(menu_choice)],
            WAIT_ZIP: [MessageHandler(filters.Document.ALL, handle_zip), CallbackQueryHandler(menu_choice)],
            WAIT_API_CPM1_CREDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_cpm1_creds), CallbackQueryHandler(menu_choice)],
            WAIT_API_CPM2_CREDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_cpm2_creds), CallbackQueryHandler(menu_choice)],
            WAIT_FARM_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_farm_email), CallbackQueryHandler(menu_choice)],
            WAIT_FARM_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_farm_password), CallbackQueryHandler(menu_choice)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start), CallbackQueryHandler(menu_choice)],
        per_chat=True, per_message=False,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("prices", prices_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("addcoins", addcoins_command))
    app.add_handler(CommandHandler("setcoins", set_coins_command))
    app.add_handler(CommandHandler("unlimited", unlimited_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("stopbot", stopbot_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_error_handler(error_handler)

    class Health(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b'OK')
        def do_HEAD(self):
            self.send_response(200); self.end_headers()

    def run_http():
        port = int(os.environ.get('PORT', 10000))
        HTTPServer(('0.0.0.0', port), Health).serve_forever()

    threading.Thread(target=run_http, daemon=True).start()
    print("🤖 MARK CPM TOOL v3.0 - Multi-Language + Coin Farm + Rank")
    app.run_polling()

if __name__ == "__main__":
    main()
