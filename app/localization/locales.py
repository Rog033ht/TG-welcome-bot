from __future__ import annotations

SUPPORTED_LANGS = {"en", "ph", "vi", "es", "tr"}

# Telegram / ISO codes that should map into our locale buckets
_LANG_ALIASES: dict[str, str] = {
    "fil": "ph",  # Telegram "Filipino" -> Taglish strings (internal code ph)
}

# Old Driver terms consolidated: EN, PH, VI, ES, TR
LOCALES: dict[str, dict[str, str]] = {
    "en": {
        "WELCOME_TITLE": "Hi! Welcome to <b>Official Ecosystem</b>.",
        "WELCOME_SUB": "Pick an action below — view all commands or try a sample post.",
        "BTN_ALL_COMMANDS": "📋 All commands",
        "BTN_DEMO_POST": "🔥 Sample post",
        "BTN_TEMPLATE_MGMT": "🧩 Template manager",
        "HELP_TEMPLATE_MGMT": (
            "<b>Template Manager</b>\n\n"
            "<code>/template_list</code> — View template names\n"
            "<code>/template_save NAME</code> — Save current button layout\n"
            "<code>/template_apply NAME</code> — Apply template inside campaign flow\n"
            "<code>/template_delete NAME</code> — Delete a template\n\n"
            "Note: These are admin-only commands."
        ),
        "HELP_COMMANDS": (
            "<b>What This Bot Can Do</b>\n\n"
            "<b>User Commands</b>\n"
            "<code>/start</code> — Welcome + quick menu\n"
            "<code>/post_demo</code> — Sample post with CTA button\n"
            "<code>/spin</code> — Lucky spin (coming soon)\n\n"
            "<b>Operator Commands (Admin only)</b>\n"
            "<code>/campaign_create</code> — Build and publish campaign posts\n"
            "<code>/campaign_cancel</code> — Cancel active campaign flow\n"
            "<code>/asset_save NAME</code> — Save replied photo/video for reuse\n"
            "<code>/ops_flow</code> — Fast operation checklist\n"
            "<code>/operator_help</code> — Operator command help\n"
            "<code>/poll_create</code> — Configure 2-option smart polls (with optional asset)\n"
            "<code>/broadcast_new asset|caption</code> — Create broadcast job\n"
            "<code>/broadcast_run ID</code> — Start/resume broadcast\n"
            "<code>/broadcast_pause ID</code> — Pause broadcast\n"
            "<code>/broadcast_status ID</code> — Check broadcast progress\n\n"
            "Note: Operator commands work only for IDs in <code>ADMIN_IDS</code>."
        ),
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
        "WELCOME_SUB": "Pili ka sa buttons below — tingnan lahat ng commands o subukan ang sample post.",
        "BTN_ALL_COMMANDS": "📋 Lahat ng commands",
        "BTN_DEMO_POST": "🔥 Sample post",
        "BTN_TEMPLATE_MGMT": "🧩 Template manager",
        "HELP_TEMPLATE_MGMT": (
            "<b>Template Manager</b>\n\n"
            "<code>/template_list</code> — List ng template names\n"
            "<code>/template_save NAME</code> — Save current button layout\n"
            "<code>/template_apply NAME</code> — Apply template sa campaign flow\n"
            "<code>/template_delete NAME</code> — Delete template\n\n"
            "Note: Admin-only commands ito."
        ),
        "HELP_COMMANDS": (
            "<b>Kayang Gawin ng Bot</b>\n\n"
            "<b>User Commands</b>\n"
            "<code>/start</code> — Welcome + quick menu\n"
            "<code>/post_demo</code> — Sample post na may CTA button\n"
            "<code>/spin</code> — Lucky spin (soon pa)\n\n"
            "<b>Operator Commands (Admin lang)</b>\n"
            "<code>/campaign_create</code> — Gumawa at mag-publish ng campaign post\n"
            "<code>/campaign_cancel</code> — Kanselahin ang campaign flow\n"
            "<code>/asset_save NAME</code> — I-save ang ni-reply na photo/video\n"
            "<code>/ops_flow</code> — Mabilis na ops checklist\n"
            "<code>/operator_help</code> — Operator command help\n"
            "<code>/poll_create</code> — Setup ng 2-option smart poll (may optional asset)\n"
            "<code>/broadcast_new asset|caption</code> — Gumawa ng broadcast job\n"
            "<code>/broadcast_run ID</code> — Start/resume broadcast\n"
            "<code>/broadcast_pause ID</code> — Pause broadcast\n"
            "<code>/broadcast_status ID</code> — Tingnan ang progress\n\n"
            "Note: Yung operator commands, gagana lang sa IDs na nasa <code>ADMIN_IDS</code>."
        ),
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
        "WELCOME_SUB": "Chon ben duoi: xem tat ca lenh hoac thu bai demo.",
        "BTN_ALL_COMMANDS": "📋 Tat ca lenh",
        "BTN_DEMO_POST": "🔥 Bai demo",
        "BTN_TEMPLATE_MGMT": "🧩 Quan ly template",
        "HELP_TEMPLATE_MGMT": (
            "<b>Quan Ly Template</b>\n\n"
            "<code>/template_list</code> — Xem danh sach template\n"
            "<code>/template_save NAME</code> — Luu bo cuc buttons hien tai\n"
            "<code>/template_apply NAME</code> — Ap dung template trong campaign\n"
            "<code>/template_delete NAME</code> — Xoa template\n\n"
            "Luu y: Lenh chi danh cho admin."
        ),
        "HELP_COMMANDS": (
            "<b>Chuc Nang Bot</b>\n\n"
            "<b>Lenh nguoi dung</b>\n"
            "<code>/start</code> — Chao mung + menu nhanh\n"
            "<code>/post_demo</code> — Bai mau co nut CTA\n"
            "<code>/spin</code> — Vong quay (sap co)\n\n"
            "<b>Lenh operator (chi Admin)</b>\n"
            "<code>/campaign_create</code> — Tao va dang bai campaign\n"
            "<code>/campaign_cancel</code> — Huy campaign dang thao tac\n"
            "<code>/asset_save NAME</code> — Luu photo/video da reply de tai su dung\n"
            "<code>/ops_flow</code> — Checklist van hanh nhanh\n"
            "<code>/operator_help</code> — Tro giup lenh operator\n"
            "<code>/poll_create</code> — Cau hinh smart poll 2 lua chon (co the gan asset)\n"
            "<code>/broadcast_new asset|caption</code> — Tao job broadcast\n"
            "<code>/broadcast_run ID</code> — Chay/tiep tuc broadcast\n"
            "<code>/broadcast_pause ID</code> — Tam dung broadcast\n"
            "<code>/broadcast_status ID</code> — Xem tien do\n\n"
            "Luu y: Lenh operator chi hoat dong voi ID trong <code>ADMIN_IDS</code>."
        ),
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
        "WELCOME_SUB": "Elige abajo: ver todos los comandos o probar un post de ejemplo.",
        "BTN_ALL_COMMANDS": "📋 Todos los comandos",
        "BTN_DEMO_POST": "🔥 Post de ejemplo",
        "BTN_TEMPLATE_MGMT": "🧩 Gestor de plantillas",
        "HELP_TEMPLATE_MGMT": (
            "<b>Gestor de Plantillas</b>\n\n"
            "<code>/template_list</code> — Ver nombres de plantillas\n"
            "<code>/template_save NAME</code> — Guardar layout de botones actual\n"
            "<code>/template_apply NAME</code> — Aplicar plantilla en flujo campaign\n"
            "<code>/template_delete NAME</code> — Eliminar plantilla\n\n"
            "Nota: Comandos solo para admin."
        ),
        "HELP_COMMANDS": (
            "<b>Funciones Del Bot</b>\n\n"
            "<b>Comandos de usuario</b>\n"
            "<code>/start</code> — Bienvenida + menu rapido\n"
            "<code>/post_demo</code> — Post de ejemplo con boton CTA\n"
            "<code>/spin</code> — Ruleta (muy pronto)\n\n"
            "<b>Comandos de operador (solo Admin)</b>\n"
            "<code>/campaign_create</code> — Crear y publicar campana\n"
            "<code>/campaign_cancel</code> — Cancelar flujo de campana\n"
            "<code>/asset_save NAME</code> — Guardar foto/video respondido para reutilizar\n"
            "<code>/ops_flow</code> — Checklist operativo rapido\n"
            "<code>/operator_help</code> — Ayuda de comandos operador\n"
            "<code>/poll_create</code> — Configurar encuesta 2 opciones (con asset opcional)\n"
            "<code>/broadcast_new asset|caption</code> — Crear trabajo de broadcast\n"
            "<code>/broadcast_run ID</code> — Iniciar/reanudar broadcast\n"
            "<code>/broadcast_pause ID</code> — Pausar broadcast\n"
            "<code>/broadcast_status ID</code> — Ver progreso\n\n"
            "Nota: Los comandos de operador solo funcionan para IDs en <code>ADMIN_IDS</code>."
        ),
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
        "WELCOME_SUB": "Asagidan sec: tum komutlar veya ornek bir gonderi.",
        "BTN_ALL_COMMANDS": "📋 Tum komutlar",
        "BTN_DEMO_POST": "🔥 Ornek gonderi",
        "BTN_TEMPLATE_MGMT": "🧩 Template yonetimi",
        "HELP_TEMPLATE_MGMT": (
            "<b>Template Yonetimi</b>\n\n"
            "<code>/template_list</code> — Template adlarini listele\n"
            "<code>/template_save NAME</code> — Mevcut buton duzenini kaydet\n"
            "<code>/template_apply NAME</code> — Campaign akisi icinde template uygula\n"
            "<code>/template_delete NAME</code> — Template sil\n\n"
            "Not: Bu komutlar sadece admin icindir."
        ),
        "HELP_COMMANDS": (
            "<b>Bot Ozellikleri</b>\n\n"
            "<b>Kullanici komutlari</b>\n"
            "<code>/start</code> — Hos geldin + hizli menu\n"
            "<code>/post_demo</code> — CTA dugmeli ornek gonderi\n"
            "<code>/spin</code> — Sans carki (yakinda)\n\n"
            "<b>Operator komutlari (sadece Admin)</b>\n"
            "<code>/campaign_create</code> — Kampanya gonderisi olustur ve yayinla\n"
            "<code>/campaign_cancel</code> — Aktif kampanya akisina son ver\n"
            "<code>/asset_save NAME</code> — Yanitlanan foto/video kaydet\n"
            "<code>/ops_flow</code> — Hizli operasyon akisi\n"
            "<code>/operator_help</code> — Operator komut yardimi\n"
            "<code>/poll_create</code> — Iki secenekli smart poll tanimla (opsiyonel asset ile)\n"
            "<code>/broadcast_new asset|caption</code> — Broadcast isi olustur\n"
            "<code>/broadcast_run ID</code> — Broadcast baslat/devam et\n"
            "<code>/broadcast_pause ID</code> — Broadcast duraklat\n"
            "<code>/broadcast_status ID</code> — Ilerlemeyi gor\n\n"
            "Not: Operator komutlari yalnizca <code>ADMIN_IDS</code> icindeki ID'lerde calisir."
        ),
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

# Global "Old Driver" marketing term bank (2026)
# Dimensions: core conversion, sports betting, rebate/cashback, finance/trust.
TERM_BANK: dict[str, dict[str, dict[str, str]]] = {
    "core": {
        "ELITE_ACTION": {
            "en": "Elite Action",
            "ph": "Lodi Logic",
            "vi": "Dan Choi VIP",
            "es": "Accion Pro",
            "tr": "Baba VIP",
        },
        "JOIN_NOW": {
            "en": "Join Now",
            "ph": "Sali na, Lodi",
            "vi": "Tham gia ngay",
            "es": "Unete ya",
            "tr": "Hemen Cok",
        },
        "REGISTER_NOW": {
            "en": "Register",
            "ph": "Mag-Register na",
            "vi": "Dang ky ngay",
            "es": "Registrate",
            "tr": "Kayit Patlat",
        },
        "PLAY_NOW": {
            "en": "Play Now",
            "ph": "Laro na",
            "vi": "Chien luon",
            "es": "Jugar ahora",
            "tr": "Oyuna Gir",
        },
    },
    "sports": {
        "SPORTSBOOK": {
            "en": "Sports Betting",
            "ph": "Sports Betting",
            "vi": "Keo Thom",
            "es": "Pasion Futbolera",
            "tr": "Mac Gunu",
        },
        "BEST_ODDS": {
            "en": "God-tier Odds",
            "ph": "Malakas na Odds",
            "vi": "Ty le Xanh Chin",
            "es": "Cuotas de Infarto",
            "tr": "Bomlu Oranlar",
        },
        "LIVE_BETTING": {
            "en": "Live Betting",
            "ph": "Live na Pagtaya",
            "vi": "Cuoc Truc Tiep",
            "es": "Apuestas en Vivo",
            "tr": "Canli Bahis",
        },
        "TODAYS_MATCH": {
            "en": "Today's Match",
            "ph": "Laro Ngayon",
            "vi": "Tran dinh hom nay",
            "es": "Gran Partido",
            "tr": "Gunun Maci",
        },
    },
    "rebate": {
        "UNLIMITED_KICKBACK": {
            "en": "Unlimited Kickback",
            "ph": "Balik-Taya Agad",
            "vi": "Hoan Tien VIP",
            "es": "Cashback Brutal",
            "tr": "Aninda Iade",
        },
        "DAILY_REBATE": {
            "en": "Daily Rebate",
            "ph": "Araw-araw na Balik",
            "vi": "Hoan tra moi ngay",
            "es": "Reembolso Diario",
            "tr": "Gunluk Iade",
        },
        "SECOND_CHANCE": {
            "en": "Second Chance",
            "ph": "Bawi-Talo",
            "vi": "Go Gac",
            "es": "Revancha Total",
            "tr": "Kayip Telafisi",
        },
        "NO_TURNOVER": {
            "en": "No Turnover",
            "ph": "Walang Turnover",
            "vi": "Khong vong cuoc",
            "es": "Sin Rollover",
            "tr": "Cevrimsiz",
        },
    },
    "finance": {
        "SOLID_TRUST": {
            "en": "Solid Trust",
            "ph": "Pera Agad",
            "vi": "Uy Tin 100%",
            "es": "Plata o Plomo",
            "tr": "Guvenceli",
        },
        "INSTANT_OUT": {
            "en": "Instant Out",
            "ph": "Pera Agad",
            "vi": "Rut Tien Ting Ting",
            "es": "Retiro Veloz",
            "tr": "Hizli Cekim",
        },
        "MY_WALLET": {
            "en": "My Wallet",
            "ph": "Aking Wallet",
            "vi": "Vi cua toi",
            "es": "Mi Billetera",
            "tr": "Cuzdanim",
        },
        "VERIFIED": {
            "en": "Verified",
            "ph": "Legit / No Scam",
            "vi": "Da xac minh",
            "es": "Verificado",
            "tr": "Onayli Hesap",
        },
    },
}


def normalize_lang(code: str | None) -> str:
    if not code:
        return "en"
    c = code.lower().strip()
    if c in SUPPORTED_LANGS:
        return c
    c2 = c.split("-", 1)[0]
    if c in _LANG_ALIASES:
        return _LANG_ALIASES[c]
    if c2 in _LANG_ALIASES:
        return _LANG_ALIASES[c2]
    return c2 if c2 in SUPPORTED_LANGS else "en"


def t(key: str, lang: str = "en") -> str:
    l = normalize_lang(lang)
    return LOCALES.get(l, LOCALES["en"]).get(key, LOCALES["en"].get(key, key))


def term(dimension: str, key: str, lang: str = "en") -> str:
    l = normalize_lang(lang)
    block = TERM_BANK.get(dimension, {})
    entry = block.get(key, {})
    return entry.get(l) or entry.get("en") or key

