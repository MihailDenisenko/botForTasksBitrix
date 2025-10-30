import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

BOT_TOKEN = "7547628532:AAEaThTghEpeqV87qYhMr8phGaTEkYkhxhM"
PAYMENT_PROVIDER_TOKEN = "381764678:TEST:MzY4ZDUzMzQ2NTQ5"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# Кнопка оплаты
@dp.message(F.text == "/buy")
async def buy(message: types.Message):
    message.answer("Otvet")
    prices = [types.LabeledPrice(label="Товар 1", amount=50000)]  # amount в копейках (500.00 ₽)

    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Оплата товара",
        description="Описание товара",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="rub",
        prices=prices,
        start_parameter="example-payment",
        payload="payload-test"
    )


# Подтверждение перед оплатой
@dp.pre_checkout_query(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# После успешной оплаты
@dp.message(F.content_type == "successful_payment")
async def process_successful_payment(message: types.Message):
    payment = message.successful_payment.to_python()
    await message.answer(f"✅ Оплата прошла успешно!\n\nДетали:\n{payment}")


async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
