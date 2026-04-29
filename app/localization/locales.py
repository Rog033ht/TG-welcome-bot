from __future__ import annotations

SUPPORTED_LANGS = {"en", "ph", "vi", "es", "tr"}

# Old Driver terms consolidated: EN, PH, VI, ES, TR
LOCALES: dict[str, dict[str, str]] = {
    "en": {
        "WELCOME_TITLE": "Hi! Welcome to <b>Official Ecosystem</b>.",
        "WELCOME_SUB": "For safety and legitimacy, use our official links below:",
        "BTN_GROUPS": "👥 Groups / Community",
        "BTN_APP": "📲 App Download",
        "BTN_OFFICIAL_BOT": "🤖 Official Bot",
        "BTN_SUPPORT": "🧑‍💻 Support / Help",
        "SPIN_TITLE": "🎡 Lucky Spin",
        "SPIN_SOON": "Lucky Spin is coming soon. We are preparing rewards.",
        "POST_CTA": "👇 Want to react? Leave a comment:",
        "BTN_LEAVE_COMMENT": "💬 Leave a Comment",
    },
    "ph": {
        "WELCOME_TITLE": "Hi! Welcome sa <b>Official Ecosystem</b>.",
        "WELCOME_SUB": "Para safe at legit, dito ka na sa official links namin.\n\nPili ka lang sa menu below:",
        "BTN_GROUPS": "👥 Groups / Community",
        "BTN_APP": "📲 App Download",
        "BTN_OFFICIAL_BOT": "🤖 Official Bot",
        "BTN_SUPPORT": "🧑‍💻 Support / Help",
        "SPIN_TITLE": "🎡 Lucky Spin",
        "SPIN_SOON": "Soon pa 'to, boss. Inaayos pa namin para solid yung rewards.",
        "POST_CTA": "👇 Gusto mo mag-react? Comment ka dito:",
        "BTN_LEAVE_COMMENT": "💬 Leave a Comment",
    },
    "vi": {
        "WELCOME_TITLE": "Xin chao! Chao mung ban den voi <b>Official Ecosystem</b>.",
        "WELCOME_SUB": "De an toan va chinh thong, vui long dung cac link chinh thuc ben duoi:",
        "BTN_GROUPS": "👥 Nhom / Cong dong",
        "BTN_APP": "📲 Tai ung dung",
        "BTN_OFFICIAL_BOT": "🤖 Bot chinh thuc",
        "BTN_SUPPORT": "🧑‍💻 Ho tro",
        "SPIN_TITLE": "🎡 Vong quay may man",
        "SPIN_SOON": "Tinh nang nay sap mo. Dang chuan bi phan thuong.",
        "POST_CTA": "👇 Muon tuong tac? De lai binh luan:",
        "BTN_LEAVE_COMMENT": "💬 De lai binh luan",
    },
    "es": {
        "WELCOME_TITLE": "Hola! Bienvenido a <b>Official Ecosystem</b>.",
        "WELCOME_SUB": "Para mantenerte seguro, usa nuestros enlaces oficiales:",
        "BTN_GROUPS": "👥 Grupos / Comunidad",
        "BTN_APP": "📲 Descargar app",
        "BTN_OFFICIAL_BOT": "🤖 Bot oficial",
        "BTN_SUPPORT": "🧑‍💻 Soporte / Ayuda",
        "SPIN_TITLE": "🎡 Ruleta de suerte",
        "SPIN_SOON": "Muy pronto. Estamos preparando las recompensas.",
        "POST_CTA": "👇 Quieres reaccionar? Deja un comentario:",
        "BTN_LEAVE_COMMENT": "💬 Dejar comentario",
    },
    "tr": {
        "WELCOME_TITLE": "Merhaba! <b>Official Ecosystem</b>'e hos geldin.",
        "WELCOME_SUB": "Guvenlik icin resmi linkleri kullan:",
        "BTN_GROUPS": "👥 Gruplar / Topluluk",
        "BTN_APP": "📲 Uygulamayi indir",
        "BTN_OFFICIAL_BOT": "🤖 Resmi bot",
        "BTN_SUPPORT": "🧑‍💻 Destek / Yardim",
        "SPIN_TITLE": "🎡 Sans Carki",
        "SPIN_SOON": "Cok yakinda. Oduller hazirlaniyor.",
        "POST_CTA": "👇 Tepki vermek ister misin? Yorum birak:",
        "BTN_LEAVE_COMMENT": "💬 Yorum birak",
    },
}


def normalize_lang(code: str | None) -> str:
    if not code:
        return "en"
    c = code.lower().strip()
    if c in SUPPORTED_LANGS:
        return c
    c2 = c.split("-", 1)[0]
    return c2 if c2 in SUPPORTED_LANGS else "en"


def t(key: str, lang: str = "en") -> str:
    l = normalize_lang(lang)
    return LOCALES.get(l, LOCALES["en"]).get(key, LOCALES["en"].get(key, key))

