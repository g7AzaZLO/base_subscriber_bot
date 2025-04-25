from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.channel import check_user_subscription, create_channels_keyboard
from handlers.wallets import WalletStates
from utils.metrics import add_user

standart_router = Router()

@standart_router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик /start:
    — если пользователь не подписан на все каналы, предлагает подписаться;
    — иначе сразу просит прислать список кошельков и переводит FSM в состояние ожидания.
    """
    await state.clear()
    user_id: int = message.from_user.id

    not_subscribed: list[str] = await check_user_subscription(user_id)
    if not_subscribed:
        keyboard = await create_channels_keyboard(
            not_subscribed,
            include_subscribed_button=True
        )
        await message.answer(
            "Подпишитесь на каналы ниже, чтобы получить доступ:",
            reply_markup=keyboard
        )
    else:
        add_user(user_id)
        # Пользователь уже подписан
        await message.answer("Вы подписаны")
        await message.answer(
            "Пришлите свои кошельки в формате:\n"
            "0xКошелек1\n"
            "0xКошелек2\n"
            "0xКошелек3\n..."
        )
        await state.set_state(WalletStates.waiting_for_wallets)