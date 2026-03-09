import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    WebAppInfo, 
    LabeledPrice, 
    PreCheckoutQuery, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

# --- НАЛАШТУВАННЯ ---
TOKEN = "8593665111:AAEcL1UIdI-hBKn_BR5QIkJyxyO4AOYCR-o"

# ТУТ ВСТАВИШ ПОСИЛАННЯ, ЯКЕ ДАСТЬ GITHUB PAGES (наприклад: https://твійнік.github.io/назва-репозиторію/)
WEBAPP_URL = "ВСТАВ_ПОСИЛАННЯ_СЮДИ" 

# Логування для відстеження помилок у консолі Render
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ПРИВІТАННЯ ТА ГОЛОВНЕ МЕНЮ ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Створюємо кнопку для відкриття ігрового інтерфейсу (Web App)
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Грати в kaifrandom 🤤", 
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(
                text="Купити kaifkoin ✨", 
                callback_data="buy_menu"
            )
        ],
        [
            InlineKeyboardButton(
                text="Допомога / Інфо ℹ️", 
                callback_data="info"
            )
        ]
    ])

    await message.answer(
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        "Ласкаво просимо до **kaifrandom** — місця, де панує азарт та 🤤!\n\n"
        "💰 Заробляй $kaifkoin$, крути кейси та виводь справжні подарунки в Telegram.\n"
        "🎮 Натискай кнопку нижче, щоб відкрити ігровий центр!",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# --- МЕНЮ ПОПОВНЕННЯ (TELEGRAM STARS) ---
@dp.callback_query(F.data == "buy_menu")
async def show_buy_menu(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="100 🤤 (100 ⭐)", callback_data="pay_100")],
        [InlineKeyboardButton(text="500 🤤 (500 ⭐)", callback_data="pay_500")],
        [InlineKeyboardButton(text="1000 🤤 (1000 ⭐)", callback_data="pay_1000")],
        [InlineKeyboardButton(text="« Назад", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(
        "Оберіть кількість **kaifkoin** для поповнення через Telegram Stars:",
        reply_markup=markup
    )

# --- ОБРОБКА ПЛАТЕЖІВ ---
@dp.callback_query(F.data.startswith("pay_"))
async def send_invoice(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[1])
    
    # Створюємо рахунок для оплати зірочками (currency="XTR")
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Поповнення kaifkoin",
        description=f"Купівля {amount} ігрових монет для kaifrandom 🤤",
        payload=f"topup_{amount}",
        provider_token="", # Для Stars залишаємо порожнім
        currency="XTR",
        prices=[LabeledPrice(label="kaifkoin", amount=amount)]
    )
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    # Підтверджуємо, що готові прийняти платіж
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def success_payment_handler(message: types.Message):
    # Сюди можна додати логіку збереження балансу в базу даних
    amount = message.successful_payment.total_amount
    await message.answer(
        f"✅ Успішно! На твій ігровий баланс зараховано **{amount} kaifkoin** 🤤.\n"
        "Приємної гри!"
    )

# --- ДОДАТКОВІ ФУНКЦІЇ ---
@dp.callback_query(F.data == "info")
async def show_info(callback: types.CallbackQuery):
    text = (
        "📜 **Правила гри:**\n"
        "1. Купуй $kaifkoin$ за зірочки.\n"
        "2. Вигравай $kaifbablo$ у кейсах або КНП.\n"
        "3. Мінімальний вивід — 1000 $kaifbablo$.\n\n"
        "⚠️ Залишок при виводі менше 15 монет автоматично анулюється.\n"
        "🎁 Вивід здійснюється реальними Telegram-подарунками!"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Назад", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    # Повертаємо початкове повідомлення (просто викликаємо функцію, що схожа на старт)
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Грати в kaifrandom 🤤", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="Купити kaifkoin ✨", callback_data="buy_menu")],
        [InlineKeyboardButton(text="Допомога / Інфо ℹ️", callback_data="info")]
    ])
    await callback.message.edit_text("Головне меню kaifrandom:", reply_markup=markup)

# --- ЗАПУСК ---
async def main():
    print("Бот запущений і готовий до роботи!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот зупинений")
