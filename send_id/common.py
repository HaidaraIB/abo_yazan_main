from telegram.ext import ContextTypes
from PyroClientSingleton import PyroClientSingleton
import asyncio
from DB import DB
from common import edit_message_text
import os


def extract_important_info(text: str, is_closed: bool):
    important_line_names_to_numbers_mapper = {
        "id": 0,
        "country": 1,
        "registery_date": 2,
        "balance": 6,
        "deposits_count": 7,
        "deposits_sum": 8,
        "withdrawal_count": 11,
        "withdrawal_sum": 12,
        "turnover_clear": 16,
        "vol_share": 19,
    }
    if is_closed:
        important_line_names_to_numbers_mapper = {
            "id": 0,
            "country": 1,
            "registery_date": 2,
            "balance": 7,
            "deposits_count": 8,
            "deposits_sum": 9,
            "withdrawal_count": 12,
            "withdrawal_sum": 13,
            "turnover_clear": 17,
            "vol_share": 20,
        }
    all_lines = text.split("\n")
    important_lines: list[str] = []

    for line_number in important_line_names_to_numbers_mapper.values():
        try:
            important_lines.append(all_lines[line_number].split("#")[1].strip())
        except IndexError:
            try:
                important_lines.append(all_lines[line_number].split("$")[1].strip())
            except IndexError:
                try:
                    important_lines.append(all_lines[line_number].split(":")[1].strip())
                except:
                    pass

    important_lines[2] = important_lines[2][:-1]
    try:
        important_lines[-2] = (
            f"{(float(important_lines[-2].replace(',', '')) * 0.4):.2f}"
        )
        important_lines[-1] = (
            f"{(float(important_lines[-1].replace(',', '')) * 0.4):.2f}"
        )
    except ValueError:
        pass

    return important_lines


def stringify_id_info(info: list, is_closed: bool):
    return (
        f"Trader # {info[0]}\n"
        f"Counrty: {info[1]}\n"
        f"Registration Date: {info[2]}\n"
        f"{'ACCOUNT CLOSED' if is_closed else ''}\n"
        f"{'-' * 27}\n"
        f"Balance: $ {info[3]}\n"
        f"Deposit Count: {info[4]}\n"
        f"Deposit Sum: $ {info[5]}\n"
        f"Withdrawals Count: {info[6]}\n"
        f"Withdrawals Sum: $ {info[7]}\n"
        f"Turnover Clear: $ {info[8]}\n"
        f"Vol Share: $ {info[9]}\n"
        f"{'-' * 27}\n"
    )


async def get_id_info(
    context: ContextTypes.DEFAULT_TYPE,
    i: str,
    user_id: int = 6603740400,
):
    stored_id = DB.get_ids(i=i)
    if stored_id and stored_id["is_closed"]:
        return "not found"

    ids_channel_id = int(os.getenv("IDS_CHANNEL_ID"))
    cpyro = PyroClientSingleton()
    sent = await cpyro.send_message(
        chat_id="@QuotexPartnerBot",
        text=i,
    )
    await asyncio.sleep(2)
    rcvd = await cpyro.get_messages(
        chat_id="@QuotexPartnerBot",
        message_ids=sent.id + 1,
    )
    if (not rcvd.text) or ("not found" in rcvd.text) or ("Trader #" not in rcvd.text):
        return "not found"

    is_closed = "ACCOUNT CLOSED" in rcvd.text
    data = extract_important_info(rcvd.text, is_closed=is_closed)

    if "Link Id: 983427" not in rcvd.text:
        if stored_id:
            try:
                await context.bot.delete_message(
                    chat_id=ids_channel_id,
                    message_id=int(stored_id["message_id"]),
                )
            except:
                pass
            await DB.delete_id(i=i)
        remote_data = DB.get_from_remote_db(trader_id=data[0])
        if remote_data:
            DB.delete_from_remote(i=i)
        return "not found"

    if stored_id:
        if is_closed and not stored_id["is_closed"]:
            await DB.close_account(i=i)
        await DB.update_message_text(i=i, new_text="/".join(data))
        await edit_message_text(
            context=context,
            chat_id=ids_channel_id,
            message_id=int(stored_id["message_id"]),
            text="/".join(data) + (" ❌" if is_closed else ""),
        )
    else:
        msg = await context.bot.send_message(
            chat_id=ids_channel_id,
            text="/".join(data) + (" ❌" if is_closed else ""),
        )
        await DB.add_id(
            i=i,
            user_id=user_id,
            message_id=msg.id,
            message_text="/".join(data) + (" ❌" if is_closed else ""),
            is_closed=is_closed,
        )
    remote_data = DB.get_from_remote_db(trader_id=data[0])
    if remote_data:
        DB.update_into_remote_db(data=data, is_closed=int(is_closed))
    else:
        DB.insert_into_remote_db(data=data, is_closed=int(is_closed))

    return data, is_closed
