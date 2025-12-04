import requests
import time

BASE_URL = "https://blockchain.info"
BLOCK_HEIGHT = 399810


# ----------------------------- ✦ HELPERS ✦ -----------------------------
def get_json(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def get_block_by_height(height):
    url = f"{BASE_URL}/block-height/{height}?format=json"
    data = get_json(url)
    return data.get("blocks", [])[0]


def get_transaction(tx_hash):
    url = f"{BASE_URL}/rawtx/{tx_hash}"
    return get_json(url)


def sum_inputs_sats(tx):
    inputs = tx.get("inputs") or tx.get("vin") or []
    total = 0
    for inp in inputs:
        prev = inp.get("prev_out") or inp.get("prevtx") or inp.get("output")
        if not prev or ("value" not in prev and "vout" not in prev):
            return None
        val = prev.get("value")
        if val is None:
            return None
        total += int(val)
    return total


def sum_outputs_sats(tx):
    outs = tx.get("out") or tx.get("outputs") or []
    total = 0
    for o in outs:
        total += int(o.get("value", 0))
    return total


def calculate_fee(tx):
    sum_in = sum_inputs_sats(tx)
    if sum_in is None:
        return None
    sum_out = sum_outputs_sats(tx)
    fee = sum_in - sum_out if sum_in and sum_out else None
    return fee if fee and fee > 0 else None


def calculate_ratio(fee, sum_out):
    if fee is None:
        return None
    if sum_out == 0:
        return None
    return fee / sum_out


# ----------------------------- ✦ MASTER FN ✦ -----------------------------
def main():

    print(f"Проверка блока {BLOCK_HEIGHT}...")

    # ----------------------------- ✦ GLOBALS ✦ -----------------------------
    min_item = None
    max_item = None

    try:
        block = get_block_by_height(BLOCK_HEIGHT)
        txs = block.get("tx", [])

        if not txs:
            print("В блоке нет транзакций или АПИ вернул что-то странное 👻")
            return

        # ----------------------------- ✦ SET UP ✦ -----------------------------
        for short_tx in txs:
            txid = short_tx.get("hash") or short_tx.get("txid")
            if not txid:
                continue

            try:
                tx = get_transaction(txid)
            except Exception as e:
                print(f"Не получилось забрать данные о транзакции 😥 {txid}: {e}")
                time.sleep(0.1)
                continue

            # ----------------------------- ✦ MATH ✦ -----------------------------
            # fee = tx.get("fee") # из АПИ
            fee = calculate_fee(tx)
            print(fee)
            sum_out = sum_outputs_sats(tx)
            print(sum_out)
            ratio = calculate_ratio(fee, sum_out)
            print(ratio)

            if fee is None or ratio is None:
                time.sleep(0.1)
                continue

            item = (ratio, txid, fee, sum_out)

            # ----------------------------- ✦ SORT ✦ -----------------------------
            if min_item is None or item[0] < min_item[0]:
                min_item = item
            if max_item is None or item[0] > max_item[0]:
                max_item = item

            time.sleep(0.1)

        # ----------------------------- ✦ RESULTS ✦ -----------------------------
        print(
            "----------------------------- ✦ РЕЗУЛЬТАТЫ ✦ -----------------------------"
        )
        if min_item:
            ratio, txid, fee_sats, sum_out_sats = min_item
            print("Транзакция с МИНИМАЛЬНЫМ отношением комиссии к сумме:")
            print(f"TXID: {txid}")
            print(f"Комиссия: {fee_sats} сатоши")
            print(f"Сумма: {sum_out_sats} сатоши")
            print(f"Коэффициент: {ratio:.8f}\n")
        else:
            print("Не удалось найти транзакцию с минимальным коэффициентом.\n")

        if max_item:
            ratio, txid, fee_sats, sum_out_sats = max_item
            print("Транзакция с МАКСИМАЛЬНЫМ отношением комиссии к сумме:")
            print(f"TXID: {txid}")
            print(f"Комиссия: {fee_sats} сатоши")
            print(f"Сумма: {sum_out_sats} сатоши")
            print(f"Коэффициент: {ratio:.8f}")
        else:
            print("Не удалось найти транзакцию с максимальным коэффициентом.")

    except Exception as e:
        print(f"ОШИБКА {BLOCK_HEIGHT}: {e}\n")


if __name__ == "__main__":
    # ----------------------------- ✦ INIT ✦ -----------------------------
    main()
