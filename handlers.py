from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bitrix_client import *
from keyboards import *





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-напоминалка лидов Bitrix24.\n\nВыберите действие из меню:",
        reply_markup=main_menu_keyboard()
    )
async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leads = get_old_leads()
    if not leads:
        await update.message.reply_text("Все лиды были обработаны")
        return

    for lead in leads:
        phone = lead.get("PHONE", "")
        text = f"Lead #{lead['ID']}\nИмя: {lead['NAME']}\nТелефон: {phone}"
        await update.message.reply_text(text, reply_markup=lead_keyboard(lead["ID"]))



async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    def safe_edit(text, reply_markup=None):
        """
        Безопасно редактирует сообщение: проверяет, отличается ли текст или клавиатура
        """
        if query.message.text != text or query.message.reply_markup != reply_markup:
            return query.edit_message_text(text, reply_markup=reply_markup)

    # Главное меню
    if query.data == "back_to_menu":
        await safe_edit(
            "Главное меню:\nВыберите действие из меню:",
            reply_markup=main_menu_keyboard()
        )
        return

    if query.data.startswith("menu:"):
        menu_type = query.data.split(":")[1]

        if menu_type == "old":
            leads = get_old_leads()
            if not leads:
                await safe_edit(
                    "Нет необработанных лидов за последние 2 часа.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]])
                )
                return

            for lead in leads:
                phone = lead.get("PHONE", "—")
                text = f"Lead #{lead['ID']}\nИмя: {lead['NAME']}\nТелефон: {phone}"
                await query.message.reply_text(
                    text,
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("✅ Called", callback_data=f"called:{lead['ID']}"),
                            InlineKeyboardButton("💬 Wrote", callback_data=f"wrote:{lead['ID']}"),
                            InlineKeyboardButton("⏳ Postpone 2h", callback_data=f"postpone:{lead['ID']}"),
                            InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
                        ]
                    ])
                )

        elif menu_type == "in_process":
            leads = get_leads_by_status("IN_PROCESS")
            if not leads:
                text = "Лидов в обработке нет."
            else:
                text = "Лиды в обработке:\n\n" + "\n".join(f"#{l['ID']} {l['NAME']} | Телефон: {l['PHONE']}" for l in leads)

            await safe_edit(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]])
            )

        elif menu_type == "postponed":
            leads = get_leads_by_status("POSTPONED")
            if not leads:
                text = "Отложенных лидов нет."
            else:
                text = "Отложенные лиды:\n\n" + "\n".join(f"#{l['ID']} {l['NAME']} | Телефон: {l['PHONE']}" for l in leads)

            await safe_edit(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]])
            )
    elif query.data.startswith(("called:", "wrote:", "postpone:")):
        try:
            action, lead_id = query.data.split(":")
        except ValueError:
            await safe_edit("Неправильная кнопка")
            return

        if action.strip().lower() == "called":
            update_lead_status(lead_id, "IN_PROCESS")
            add_comment_to_lead(lead_id, "Menedger called")
            await safe_edit(f"Lead #{lead_id} → ✅ Отмечен как 'Called'")

        elif action.strip().lower() == "wrote":
            update_lead_status(lead_id, "IN_PROCESS")
            add_comment_to_lead(lead_id, "Menedger wrote")
            await safe_edit(f"Lead #{lead_id} → 💬 Отмечен как 'Wrote'")


        elif action == "postpone":
            resp = postpone_lead_task(lead_id, minutes=120)
            update_lead_status(lead_id, "POSTPONED")
            add_comment_to_lead(lead_id, "Лид отложен на 2 часа")

            task_id = resp.get("result", {}).get("task", {}).get("id")
            if task_id:
                await query.edit_message_text(
                    f"Lead #{lead_id} → ⏳ Отложен на 2 часа (Task ID: {task_id})"
                )
            else:
                await query.edit_message_text(f"Ошибка при создании задачи для Lead #{lead_id}")