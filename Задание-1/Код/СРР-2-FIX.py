# ----------------------------- ✦ IMPS ✦ -----------------------------
import requests

# ----------------------------- ✦ GLOBS ✦ -----------------------------
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
    return data["blocks"][0]


def is_coinbase(tx):
    inputs = tx.get("inputs", [])
    return len(inputs) == 1 and "coinbase" in inputs[0]


def sum_outputs_sats(tx):
    return sum(out.get("value", 0) for out in tx.get("out", []))


# ----------------------------- ✦ MASTER FN ✦ -----------------------------
def main():
    try:
        print(f"Проверка блока {BLOCK_HEIGHT}...")

        block = get_block_by_height(BLOCK_HEIGHT)
        transactions = block.get("tx", [])

        min_item = None
        max_item = None

        for tx in transactions:
            if is_coinbase(tx):
                continue

            fee = tx.get("fee")
            if fee is None or fee <= 0:
                continue

            total_output = sum_outputs_sats(tx)
            if total_output <= 0:
                continue

            ratio = fee / total_output
            txid = tx.get("hash")

            item = (ratio, txid, fee, total_output)

            if min_item is None or ratio < min_item[0]:
                min_item = item

            if max_item is None or ratio > max_item[0]:
                max_item = item

        print(
            "----------------------------- ✦ РЕЗУЛЬТАТЫ ✦ -----------------------------"
        )

        if min_item:
            ratio, txid, fee, total = min_item
            print("Транзакция с МИНИМАЛЬНЫМ отношением комиссии к сумме:")
            print(f"TXID: {txid}")
            print(f"Комиссия: {fee} Cатоши")
            print(f"Сумма: {total} Cатоши")
            print(f"Коэффициент: {ratio:.8f}\n")
        else:
            print("Не удалось найти транзакцию с минимальным коэффициентом.\n")

        if max_item:
            ratio, txid, fee, total = max_item
            print("Транзакция с МАКСИМАЛЬНЫМ отношением комиссии к сумме:")
            print(f"TXID: {txid}")
            print(f"Комиссия: {fee} Cатоши")
            print(f"Сумма: {total} Cатоши")
            print(f"Коэффициент: {ratio:.8f}")
        else:
            print("Не удалось найти транзакцию с максимальным коэффициентом.")
    except Exception as e:
        print(f"ОШИБКА {BLOCK_HEIGHT}: {e}\n")


if __name__ == "__main__":
    main()
