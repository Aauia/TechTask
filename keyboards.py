from telegram import InlineKeyboardButton, InlineKeyboardMarkup



# Главное меню
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🆕 Необработанные лиды (последние 2 часа)", callback_data="menu:old")],
        [InlineKeyboardButton("⏳ Отложенные лиды", callback_data="menu:postponed")]
    ]
    return InlineKeyboardMarkup(keyboard)


def lead_keyboard(lead_id: str):
    keyboard = [
        [
            InlineKeyboardButton("✅ Called", callback_data=f"called:{lead_id}"),
            InlineKeyboardButton("💬 Wrote", callback_data=f"wrote:{lead_id}"),
            InlineKeyboardButton("⏳ Postpone 2h", callback_data=f"postpone:{lead_id}"),
            InlineKeyboardButton("🔙 Назад", callback_data="back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
