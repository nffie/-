import requests
import time

BASE_URL = "https://blockchain.info"
START_BLOCK = 0
END_BLOCK = 99


# ----------------------------- ✦ HELPERS ✦ -----------------------------
def get_json(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def get_blocks_by_height(height):
    url = f"{BASE_URL}/block-height/{height}?format=json"
    data = get_json(url)
    return data.get("blocks", [])


def get_transaction(tx_hash):
    url = f"{BASE_URL}/rawtx/{tx_hash}"
    return get_json(url)


def is_transaction_spent(tx):
    for output in tx["out"]:
        if output.get("spent") is True:
            return True
    return False


# ----------------------------- ✦ MASTER FN ✦ -----------------------------
def main():

    spent_blocks = []

    for height in range(START_BLOCK, END_BLOCK + 1):

        print(f"Проверка блока {height}...")

        try:
            blocks = get_blocks_by_height(height)

            for block in blocks:

                block_hash = block["hash"]

                coinbase_txid = block["tx"][0]["hash"]

                transaction = get_transaction(coinbase_txid)

                if is_transaction_spent(transaction):
                    spent_blocks.append((height, block_hash, coinbase_txid))

                    print(
                        f"ПОТРАЧЕНО\n"
                        f"Блок: {height}\n"
                        f"Хэш: {block_hash}\n"
                        f"ID транзакции:   {coinbase_txid}\n"
                    )
                else:
                    print("НЕ ПОТРАЧЕНО")

            time.sleep(1)

        except Exception as e:
            print(f"ОШИБКА {height}: {e}\n")

    # ----------------------------- ✦ RESULTS ✦ -----------------------------
    print("----------------------------- ✦ РЕЗУЛЬТАТ ✦ -----------------------------")

    for height, block_hash, txid in spent_blocks:
        print(f"\nБлок: {height}")
        print(f"{'Хэш'}:  {block_hash}")
        print(f"ID транзакции:  {txid}")

    print(f"\nОбщее кол-во потраченных коинбэйс-транзакций: {len(spent_blocks)}")


if __name__ == "__main__":
    # ----------------------------- ✦ INIT ✦ -----------------------------
    main()
