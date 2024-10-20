import asyncio
import re
from telethon import TelegramClient, functions, types


accounts = [
    {
        "api_id": "23169896",
        "api_hash": "c83d7ac378acfd5d69c2cf2e9b121e7f",
        "phone": "+77766349341",
    },
    {
        "api_id": "17086106",
        "api_hash": "1bb38ac13a669b310a3546f46e310459",
        "phone": "+77765139878",
    },
    {
        "api_id": "17811521",
        "api_hash": "6709d162077042884a1b42d6de0517f9",
        "phone": "+77052389250",
    },
    {
        "api_id": "29230035",
        "api_hash": "4f586253bd19dc97a27c28dce5d32bcb",
        "phone": "+79867555814",
    },
    {
        "api_id": "20234972",
        "api_hash": "12895a62b4007cdd682b6e78dfdfd95a",
        "phone": "+79200272786",
    },
    {
        "api_id": "20212631",
        "api_hash": "5e6bb0012cb4d0acc015b73a90e4dae2",
        "phone": "+79306669517",
    },
]


reasons = [
    types.InputReportReasonSpam(),
    types.InputReportReasonViolence(),
    types.InputReportReasonPornography(),
    types.InputReportReasonChildAbuse(),
    types.InputReportReasonIllegalDrugs(),
    types.InputReportReasonPersonalDetails(),
    types.InputReportReasonOther(),
]

reason_descriptions = [
    "Спам",
    "Насилие",
    "Порнография",
    "Детская порнография",
    "Наркотики",
    "Личные данные",
    "Другое",
]

# Функция для авторизации аккаунта с принудительной отправкой кода на номер телефона
async def login(client, phone):
    await client.start(phone=phone, force_sms=True)
    print(f"[INFO] Успешно авторизован {phone}")

# Функция для отправки одной жалобы на сообщение пользователя
async def send_report(client, user_entity, message_id, reason):
    try:
        await client(functions.messages.ReportRequest(
            peer=user_entity,
            id=[message_id],
            reason=reason,
            message="Это сообщение содержит спам."
        ))
        print(f"[INFO] Жалоба на сообщение {message_id} отправлена с аккаунта {client.session.filename}.")
        await asyncio.sleep(1)  # Пауза 1 секунда между отправками
    except Exception as e:
        print(f"[ERROR] Ошибка отправки жалобы с {client.session.filename}: {e}")

# Функция для разбора ссылки и получения чата и номера сообщения
def parse_message_link(message_link):
    pattern = r"https://t\.me/([^/]+)/(\d+)"
    match = re.match(pattern, message_link)
    if match:
        chat = match.group(1)
        message_id = int(match.group(2))
        return chat, message_id
    else:
        return None, None

# Функция для отправки жалобы с одного аккаунта на одну ссылку
async def report_spam_by_link(client, message_link, reason):
    chat, message_id = parse_message_link(message_link)
    if not chat or not message_id:
        print(f"[ERROR] Невозможно обработать ссылку {message_link}")
        return

    await asyncio.sleep(1)  # Задержка 1 секунда перед получением сообщения
    try:
        entity = await client.get_entity(chat)
        print(f"[INFO] Получена сущность чата: {entity}")
        message = await client.get_messages(entity, ids=message_id)
        if message:
            await send_report(client, entity, message.id, reason)  # Одна жалоба с одного аккаунта
        else:
            print(f"[ERROR] Сообщение с ID {message_id} не найдено в чате {chat}.")
    except Exception as e:
        print(f"[ERROR] Ошибка обработки ссылки {message_link}: {e}")

# Основная функция для авторизации всех аккаунтов и отправки жалоб
async def main():
    message_links = input("Введите ссылки на сообщения для отправки жалобы (через запятую): ").split(',')
    print("Выберите причину жалобы:")
    for i, description in enumerate(reason_descriptions, start=1):
        print(f"{i} - {description}")

    reason_choice = input("Ваш выбор: ")
    if not reason_choice.isdigit() or not (1 <= int(reason_choice) <= len(reasons)):
        print("Неверный выбор!")
        return

    selected_reason = reasons[int(reason_choice) - 1]
    clients = []

    for account in accounts:
        client = TelegramClient(f'session_{account["phone"]}', account["api_id"], account["api_hash"])
        try:
            await login(client, account["phone"])
            clients.append(client)
        except Exception as e:
            print(f"[ERROR] Ошибка авторизации для номера {account['phone']}: {e}")
            continue

    for message_link in message_links:
        for client in clients:
            await report_spam_by_link(client, message_link.strip(), selected_reason)
            await asyncio.sleep(1)

    for client in clients:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
