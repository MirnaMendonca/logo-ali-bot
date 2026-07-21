import os

from dotenv import load_dotenv

load_dotenv()

# ============================
# Discord
# ============================

TOKEN = os.getenv("DISCORD_TOKEN")

DESCOMPLICA_GUILD_ID = 1521632374721347664
# RAFAEL_GUILD_ID = ...
# LUAN_GUILD_ID = ...
# CLAUDIA_GUILD_ID = ...
# LUCIANO_GUILD_ID = ...

GUILDS = {
    DESCOMPLICA_GUILD_ID: {
        "dispatcher_name": "descomplica",
        "pf_price": 118,
    },
    # RAFAEL_GUILD_ID: {
    #     "dispatcher_name": "rafael",
    #     "pf_price": 130,
    # },
    # LUAN_GUILD_ID: {
    #     "dispatcher_name": "luan",
    #     "pf_price": 135,
    # },
    # CLAUDIA_GUILD_ID: {
    #     "dispatcher_name": "claudia",
    #     "pf_price": 135,
    # },
    # LUCIANO_GUILD_ID: {
    #     "dispatcher_name": "luciano",
    #     "pf_price": 130,
    # },
}

# ============================
# Cargos
# ============================

USER_ROLES = {"dispatcher": "Despachante", "operator": "Operador", "admin": "Admin"}

# ============================
# Google Sheets
# ============================

GOOGLE_SHEETS_ID = "1Fpnbl-OV9NMQyRcU821sI0sXemSLzVGPaLEGzU2X2zc"

# ============================
# Valores
# ============================

COURSE_PRICE = 10

PF_OPERATOR_VALUE = 5

PJ_OPERATOR_VALUE_CAD_OR_REVAL = 10
PJ_OPERATOR_VALUE_ALT_OR_REM = 5

PJ_REFUND_VALUE_CAD_OR_REVAL = 40
PJ_REFUND_VALUE_ALT_OR_REM = 10
