from decimal import Decimal
import asyncio
import re
from typing import List, Dict

import httpx
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from settings import RPC_URL
from utils.metrics import add_wallets
wallets_router: Router = Router()


class WalletStates(StatesGroup):
    waiting_for_wallets: State = State()


# шаблон Ethereum-адреса
ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")


@wallets_router.callback_query(F.data == "subscribed")
async def ask_for_wallets(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """
    После подтверждения подписки запрашиваем кошельки и переводим FSM в состояние ожидания.
    """
    prompt = (
        "Пришлите свои кошельки в формате по одному в строке, например:\n"
        "0xКошелек1\n"
        "0xКошелек2\n"
        "0xКошелек3"
    )
    await callback.message.answer(prompt)
    await state.set_state(WalletStates.waiting_for_wallets)


@wallets_router.message(WalletStates.waiting_for_wallets)
async def handle_wallets_input(
    message: types.Message,
    state: FSMContext
) -> None:
    """
    Обрабатываем список кошельков от пользователя:
    - валидируем форматы через regex;
    - запрашиваем балансы;
    - выводим построчно и сумму;
    - повторно просим кошельки.
    """
    lines = [line.strip() for line in message.text.splitlines() if line.strip()]
    # проверяем, что есть адреса и все они валидны
    invalid = [ln for ln in lines if not ADDRESS_PATTERN.fullmatch(ln)]
    if not lines or invalid:
        await message.answer(
            "Неверный формат адресов. Отправьте адреса в формате 0x... по одному в строке, например:\n"
            "0xКошелек1\n0xКошелек2"
        )
        return
    addresses: List[str] = lines
    add_wallets(len(addresses))

    balances: Dict[str, Decimal] = await fetch_balances(addresses)
    total: Decimal = sum(balances.values())

    # формируем и отправляем результат
    result_lines = [f"{addr}: {bal.normalize()} SHM" for addr, bal in balances.items()]
    result_lines.append(f"Итого: {total.normalize()} SHM")
    await message.answer("\n".join(result_lines))

    # повторный запрос кошельков
    await message.answer(
        "Пришлите ещё кошельки в том же формате или новые для следующего запроса."
    )
    # состояние остается WalletStates.waiting_for_wallets


async def get_balance_wei(address: str) -> int:
    """
    Делает JSON-RPC вызов eth_getBalance к узлу Shardeum и возвращает баланс в Wei.

    :param address: Ethereum-адрес в hex
    :return: баланс в Wei как int
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(RPC_URL, json=payload, timeout=10.0)
        resp.raise_for_status()
        result_hex: str = resp.json().get("result", "0x0")
    return int(result_hex, 16)


async def fetch_balances(addresses: List[str]) -> Dict[str, Decimal]:
    """
    Параллельно запрашивает балансы списка адресов и возвращает их в SHM.

    :param addresses: список Ethereum-адресов
    :return: словарь {address: balance в SHM}
    """
    tasks = [get_balance_wei(addr) for addr in addresses]
    wei_values = await asyncio.gather(*tasks)

    factor = Decimal(10**18)
    return {
        addr: (Decimal(wei) / factor).quantize(Decimal("0.000000000000000001"))
        for addr, wei in zip(addresses, wei_values)
    }
