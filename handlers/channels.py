from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from utils.channel import check_user_subscription, create_channels_keyboard
from handlers.wallets import WalletStates

channels_router = Router()

@channels_router.callback_query(lambda cb: cb.data == "subscribed")
async def handle_subscribed_button(
    callback_query: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    Обработчик кнопки «Я подписался»:
    — если ещё не подписан, повторяет предложение подписаться;
    — иначе сразу просит прислать список кошельков и переводит FSM в ожидание.
    """
    user_id: int = callback_query.from_user.id

    not_subscribed: list[str] = await check_user_subscription(user_id)
    if not_subscribed:
        keyboard = await create_channels_keyboard(
            not_subscribed,
            include_subscribed_button=True
        )
        await callback_query.message.answer(
            "Вы всё ещё не подписались на каналы:",
            reply_markup=keyboard
        )
    else:
        # Подписка подтвердилась — сразу запрос кошельков
        await callback_query.message.answer("Вы подписаны")
        await callback_query.message.answer(
            "Пришлите свои кошельки в формате:\n"
            "0xКошелек1\n"
            "0xКошелек2\n"
            "0xКошелек3\n..."
        )
        await state.set_state(WalletStates.waiting_for_wallets)
