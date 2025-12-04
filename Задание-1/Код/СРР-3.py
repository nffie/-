# ----------------------------- ✦ IMPS ✦ -----------------------------
import requests
from datetime import datetime, timezone

# ----------------------------- ✦ GLOBALS ✦ -----------------------------
BASE_URL = "https://blockchain.info"


# ----------------------------- ✦ HELPERS ✦ -----------------------------
def get_blocks_by_timestamp(timestamp):
    url = f"{BASE_URL}/blocks/{timestamp}?format=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_block_by_hash(block_hash):
    url = f"{BASE_URL}/rawblock/{block_hash}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# ----------------------------- ✦ MASTER FN ✦ -----------------------------
def main():
    # ----------------------------- ✦ SET UP ✦ -----------------------------
    user_date = input("Введите дату (YYYY-MM-DD): ")

    try:
        date_obj = datetime.strptime(user_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        timestamp = int(date_obj.timestamp())
    except ValueError:
        print("Ф-О-Р-М-А-Т: (YYYY-MM-DD) !!!")
        return

    try:
        blocks = get_blocks_by_timestamp(timestamp)

    except:
        print("ОШИБКА АПИ")
        return

    if not blocks:
        print("БЛОКОВ С ТАКОЙ ДАТОЙ - НЕТ")
        return

    first_10_blocks = blocks[:10]

    # ----------------------------- ✦ SCOPED GLOBALS ✦ -----------------------------
    total_transactions = 0
    total_size = 0
    block_times = []
    hashes = []
    miner_count = {}
    miner_fees = {}
    all_block_data = []

    for i, block in enumerate(first_10_blocks):
        block_hash = block["hash"]
        block_data = get_block_by_hash(block_hash)
        all_block_data.append(block_data)

        hashes.append(block_hash)

        tx_count = len(block_data["tx"])
        # -----------------------------✦ 1. сколько транзакций в них содержится? ✦ -----------------------------
        total_transactions += tx_count

        # -----------------------------✦ 2. на сколько байт увеличился размер блокчейна за счет этих блоков? ✦ -----------------------------
        total_size += block_data["size"]

        if i > 0:
            prev_time = all_block_data[i - 1]["time"]
            current_time = block_data["time"]
            block_times.append(abs(current_time - prev_time))

        coinbase_tx = block_data["tx"][0]
        output = coinbase_tx["out"]

        if output and "addr" in output[0]:
            miner_addr = output[0]["addr"]

            miner_count[miner_addr] = miner_count.get(miner_addr, 0) + 1

            total_inputs = sum(
                inp.get("prev_out", {}).get("value", 0)
                for tx in block_data["tx"][1:]
                for inp in tx["inputs"]
            )
            total_outputs = sum(
                out.get("value", 0) for tx in block_data["tx"][1:] for out in tx["out"]
            )

            fee = max(0, total_inputs - total_outputs)
            miner_fees[miner_addr] = miner_fees.get(miner_addr, 0) + fee

    # -----------------------------✦ 3. сколько времени в среднем потребовалось на генерацию одного блока? ✦ -----------------------------
    avg_block_time = sum(block_times) / len(block_times) if block_times else 0

    # -----------------------------✦ 4. какой из блоков имеет наименьший хеш? ✦ -----------------------------
    smallest_hash = min(hashes)

    fifth_block = all_block_data[4]
    total_fee_5 = 0

    total_inputs_5 = sum(
        inp.get("prev_out", {}).get("value", 0)
        for tx in fifth_block["tx"][1:]
        for inp in tx["inputs"]
    )
    total_outputs_5 = sum(
        out.get("value", 0) for tx in fifth_block["tx"][1:] for out in tx["out"]
    )

    # -----------------------------✦ 5. какой была средняя комиссия за транзакцию в 5 блоке? ✦ -----------------------------
    total_fee_5 = max(0, total_inputs_5 - total_outputs_5)
    avg_fee_5 = total_fee_5 / max(1, len(fifth_block["tx"]) - 1)

    # -----------------------------✦ 6. какой адрес сгенерировал наибольшее количество из этих блоков? (если адресов несколько, достаточно вывести первый по счёту) ✦ -----------------------------
    top_miner = max(miner_count, key=miner_count.get)

    # -----------------------------✦ 7. какой объём комиссии был получен этим адресом в дополнение к фиксированному вознаграждению? ✦ -----------------------------
    total_fees_earned = miner_fees[top_miner]

    # -----------------------------✦ 8. сколько всего транзакций совершено с участием этого адреса? ✦ -----------------------------
    address_tx_count = 0
    for block in all_block_data:
        for tx in block["tx"]:
            for out in tx["out"]:
                if out.get("addr") == top_miner:
                    address_tx_count += 1
                    break

    # ----------------------------- ✦ RESULTS ✦ -----------------------------
    print("----------------------------- ✦ РЕЗУЛЬТАТЫ ✦ -----------------------------")
    print(f"1. сколько транзакций в них содержится?: {total_transactions}")
    print(
        f"2. на сколько байт увеличился размер блокчейна за счет этих блоков?: {total_size}"
    )
    print(
        f"3. сколько времени в среднем потребовалось на генерацию одного блока?: {avg_block_time:.2f}"
    )
    print(f"4. какой из блоков имеет наименьший хеш?: {smallest_hash}")
    print(
        f"5. какой была средняя комиссия (Сатоши) за транзакцию в 5 блоке?: {avg_fee_5}"
    )
    print(
        f"6. какой адрес сгенерировал наибольшее количество из этих блоков? (если адресов несколько, достаточно вывести первый по счёту): {top_miner}"
    )
    print(
        f"7. какой объём комиссии (Сатоши) был получен этим адресом в дополнение к фиксированному вознаграждению?: {total_fees_earned}"
    )
    print(
        f"8. сколько всего транзакций совершено с участием этого адреса?: {address_tx_count}"
    )


if __name__ == "__main__":
    # ----------------------------- ✦ INIT ✦ -----------------------------
    main()
