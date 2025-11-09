import hashlib
import base58
import os
import time
import sqlite3
import multiprocessing
import threading
import random
from mnemonic import Mnemonic
from bip_utils import (
    Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip86,
    Bip44Coins, Bip49Coins, Bip84Coins, Bip86Coins, Bip44Changes
)

# --------------------------------------------------------
#               USTALENIA GLOBALNE
# --------------------------------------------------------

OUTPUT_FILE     = "znalezioneBTCALL.txt"
PROCESSES       = 3
MAX_INDEX       = 5
RESULTS_DIR     = "wyniki"
DB_FILE         = "addresses1.db"

# --------------------------------------------------------
#              POMOCNICZE FUNKCJE
# --------------------------------------------------------

def ensure_results_dir():
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

def privkey_to_wif(privkey_hex: str, compressed: bool = True) -> str:
    key_bytes = bytes.fromhex(privkey_hex)
    prefix = b'\x80' + key_bytes
    if compressed:
        prefix += b'\x01'
    checksum = hashlib.sha256(hashlib.sha256(prefix).digest()).digest()[:4]
    wif = base58.b58encode(prefix + checksum).decode()
    return wif

def address_exists_in_db(conn, address):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM addresses WHERE address = ?", (address,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"[❌] Błąd zapytania do bazy: {e}", flush=True)
        return False

def generate_hd_addresses(seed_phrase: str, max_index: int = 20) -> list:
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    results = []
    bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip49 = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
    bip84 = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    bip86 = Bip86.FromSeed(seed_bytes, Bip86Coins.BITCOIN)
    for i in range(max_index):
        for name, wallet in [("BIP44", bip44), ("BIP49", bip49), ("BIP84", bip84), ("BIP86", bip86)]:
            node = wallet.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
            address = node.PublicKey().ToAddress()
            wif = privkey_to_wif(node.PrivateKey().Raw().ToHex())
            results.append({"type": name, "index": i, "address": address, "wif": wif, "seed": seed_phrase})
    return results

# --------------------------------------------------------
#           PRODUCER: LOSOWE SEEDY Z BIP39
# --------------------------------------------------------

def seed_producer(queue, seed_counter, lock_counter):
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist

    print("[🎲] Tryb losowego generowania seedów z pełnej listy BIP39 (bez zapisu)", flush=True)

    while True:
        seed_words = random.choices(wordlist, k=12)
        phrase = " ".join(seed_words)

        if not mnemo.check(phrase):
            continue

        queue.put(phrase)

        with lock_counter:
            seed_counter.value += 1

# --------------------------------------------------------
#          WORKER: PROCES GENERUJĄCY ADRESY
# --------------------------------------------------------

def worker_process(queue, lock_io, seed_counter, address_counter, lock_counter, process_id):
    print(f"[🔁] Worker {process_id} startuje!", flush=True)
    conn = sqlite3.connect(DB_FILE)

    while True:
        seed = queue.get()
        if seed is None:
            print(f"[🏁] Worker {process_id} kończy pracę.", flush=True)
            break

        try:
            print(f"[{process_id}] 🔤 Seed: {seed}", flush=True)
            addresses = generate_hd_addresses(seed, max_index=MAX_INDEX)

            hit_found = False
            for entry in addresses:
                if address_exists_in_db(conn, entry["address"]):
                    hit_found = True
                    break

            if hit_found:
                print(f"[💥] HIT! Adres z seeda znajduje się w bazie!", flush=True)
                with lock_io:
                    with open(OUTPUT_FILE, "a", encoding="utf-8") as out_file:
                        out_file.write(f"✅ HIT!\nSeed: {seed}\n")
                        for e in addresses:
                            out_file.write(f"{e['type']}[{e['index']}]: {e['address']}\nPriv WIF: {e['wif']}\n")
                        out_file.write("------------------------------------------------------------\n\n")

            with lock_counter:
                address_counter.value += len(addresses)

        except Exception as e:
            print(f"[{process_id}] ❌ Błąd: {e}", flush=True)

# --------------------------------------------------------
#                      MAIN
# --------------------------------------------------------

if __name__ == "__main__":
    ensure_results_dir()
    print("[🚀] Start programu", flush=True)

    if not os.path.exists(DB_FILE):
        print(f"[⛔] Nie znaleziono bazy danych: {DB_FILE}", flush=True)
        exit(1)

    manager = multiprocessing.Manager()
    seed_counter = manager.Value('i', 0)
    address_counter = manager.Value('i', 0)
    lock_counter = manager.Lock()
    lock_io = manager.Lock()

    queue = multiprocessing.Queue(maxsize=PROCESSES * 2)

    producer_proc = multiprocessing.Process(
        target=seed_producer,
        args=(queue, seed_counter, lock_counter),
        name="Producer"
    )
    producer_proc.start()

    workers = []
    for i in range(PROCESSES):
        p = multiprocessing.Process(
            target=worker_process,
            args=(queue, lock_io, seed_counter, address_counter, lock_counter, i),
            name=f"Worker-{i}"
        )
        workers.append(p)
        p.start()

    def print_counters_loop():
        while True:
            with lock_counter:
                s_val = seed_counter.value
                a_val = address_counter.value
            print(f"[📈] Seedy: {s_val}, Adresy: {a_val}", flush=True)
            time.sleep(2)

    counter_thread = threading.Thread(target=print_counters_loop, daemon=True)
    counter_thread.start()

    try:
        producer_proc.join()
    except KeyboardInterrupt:
        print("[🛑] Przerwano ręcznie. Kończenie procesu...", flush=True)

    for w in workers:
        queue.put(None)
    for w in workers:
        w.join()

    print(f"[🏁] Koniec programu. Seedy: {seed_counter.value}, Adresy: {address_counter.value}", flush=True)
