import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = 'TOKEN'  # replace with your bot's API token
TINKOFF_PROVIDER_TOKEN = 'TINKOFF_PROVIDER_TOKEN_HERE'  # replace with your Tinkoff provider token

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Purchase(StatesGroup):
    waiting_for_payment = State()
    waiting_for_consultation_signup = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Create an invoice
    prices = [types.LabeledPrice(label='Webinar recording', amount=10)]  # amount is in cents
    await bot.send_invoice(chat_id=message.from_user.id,
                           title='Webinar recording',
                           description='Buy a webinar recording',
                           provider_token=TINKOFF_PROVIDER_TOKEN,
                           currency='rub',
                           is_flexible=False,  # True If you need to set up Shipping Fee
                           prices=prices,
                           start_parameter='time-machine-example',
                           payload='HAPPY FRIDAY')
    await Purchase.waiting_for_payment.set()


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=types.ContentTypes.SUCCESSFUL_PAYMENT, state=Purchase.waiting_for_payment)
async def process_successful_payment(message: types.Message):
    # If payment is successful, send the link to the recording
    await bot.send_message(chat_id=message.from_user.id,
                           text="Thanks for the purchase, here's your webinar recording: [link]")
    await Purchase.waiting_for_consultation_signup.set()


@dp.message_handler(state=Purchase.waiting_for_consultation_signup)
async def process_consultation_signup(message: types.Message):
    # Process the consultation signup here
    # Maybe save the request to the database and then send a confirmation message
    await bot.send_message(chat_id=message.from_user.id,
                           text="You've signed up for a consultation. We will contact you soon.")
    await state.finish()


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
