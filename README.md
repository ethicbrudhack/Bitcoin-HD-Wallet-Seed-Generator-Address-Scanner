# 💰 Bitcoin HD Wallet Seed Generator & Address Scanner

> ⚠️ **Educational & Security Research Tool Only**  
> This project demonstrates a **multi-process Bitcoin HD wallet generator and database address scanner**.  
> It is designed to show how **HD wallets (BIP44/BIP49/BIP84/BIP86)** derive addresses from seed phrases,  
> and how multiprocessing can be used to scan for matches efficiently.  
>  
> ❗ This program is **not for unauthorized wallet recovery or brute-forcing**.  
> Use it **only** for controlled research, security testing, or educational purposes.

---

## 🚀 Overview

This script continuously generates **random valid BIP39 seed phrases**,  
derives addresses according to **BIP44**, **BIP49**, **BIP84**, and **BIP86** standards,  
and compares them against a **local SQLite database** of known Bitcoin addresses.

When a generated address exists in the database,  
the seed and corresponding private keys are stored in a results file.

The script supports:
- 🧠 **Parallel multi-process generation**
- 🧩 **HD wallet derivation via bip_utils**
- 🗃️ **SQLite database address matching**
- 🧾 **Live statistics for seeds and addresses processed**

---

## ✨ Features

| Feature | Description |
|----------|--------------|
| 🧩 **Full HD wallet derivation** | Generates addresses for BIP44, BIP49, BIP84, BIP86 |
| 🧠 **Parallel multiprocessing** | Runs multiple worker processes concurrently |
| 🔄 **Continuous random seed generation** | Uses Mnemonic BIP39 English wordlist |
| 🧮 **SQLite database lookup** | Compares derived addresses with stored known ones |
| 📈 **Live progress display** | Displays seeds and address count every 2 seconds |
| 💾 **Result persistence** | Writes found “hits” to `znalezioneBTCALL.txt` |
| ⚙️ **Lightweight & portable** | No blockchain or network calls required |

---

## 📂 File Structure

| File | Description |
|------|-------------|
| `main.py` | Main program (this script) |
| `addresses1.db` | SQLite database containing known Bitcoin addresses |
| `znalezioneBTCALL.txt` | Output log for successful hits |
| `wyniki/` | Directory for storing results |
| `README.md` | Documentation (this file) |

---

## ⚙️ Configuration

| Variable | Purpose |
|-----------|----------|
| `OUTPUT_FILE` | Output file name for found matches |
| `PROCESSES` | Number of concurrent worker processes |
| `MAX_INDEX` | Number of derived addresses per seed (per derivation type) |
| `RESULTS_DIR` | Directory for storing results |
| `DB_FILE` | SQLite database file with known Bitcoin addresses |

**Dependencies**

pip install mnemonic bip-utils base58


---

## 🧠 How It Works

### 1️⃣ Seed Producer (Generator)

- Continuously generates **random 12-word BIP39 seed phrases**
- Validates phrases using the `mnemonic` library
- Places valid seeds into a multiprocessing queue for workers

```python
seed_words = random.choices(wordlist, k=12)
phrase = " ".join(seed_words)
if mnemo.check(phrase):
    queue.put(phrase)

2️⃣ Worker Processes

Each worker:

Retrieves a seed from the queue

Derives addresses using bip_utils for:

BIP44 (Legacy)

BIP49 (Nested SegWit)

BIP84 (Native SegWit)

BIP86 (Taproot)

Converts each private key to WIF format

Checks whether each address exists in the SQLite database

Logs all matches (“hits”) into the output file

if address_exists_in_db(conn, entry["address"]):
    with open(OUTPUT_FILE, "a") as f:
        f.write(f"✅ HIT! Seed: {seed}\n")

3️⃣ Database Query

Each worker queries:

SELECT 1 FROM addresses WHERE address = ?


If the address exists, it’s treated as a potential hit and written to the log.

4️⃣ Progress Display Thread

A background thread continuously prints current counters:

[📈] Seedy: 105, Adresy: 1890


This helps track the total number of seeds processed and addresses generated.

🧾 Example Output
[🚀] Start programu
[🎲] Tryb losowego generowania seedów z pełnej listy BIP39 (bez zapisu)
[🔁] Worker 0 startuje!
[🔁] Worker 1 startuje!
[🔁] Worker 2 startuje!
[📈] Seedy: 42, Adresy: 840
[💥] HIT! Adres z seeda znajduje się w bazie!
✅ HIT!
Seed: flat pioneer bronze ticket ...
BIP84[0]: bc1q7...
Priv WIF: L2hr1z...
------------------------------------------------------------

🧩 Core Components
Component	Function
seed_producer()	Generates and validates random BIP39 seed phrases
worker_process()	Derives HD wallet addresses and checks them in database
generate_hd_addresses()	Builds BIP44/BIP49/BIP84/BIP86 addresses for each seed
privkey_to_wif()	Converts raw private key hex → WIF
address_exists_in_db()	Checks address existence in SQLite database
print_counters_loop()	Prints live counters for progress display
⚡ Performance & Optimization Tips

Increase PROCESSES to utilize more CPU cores (default: 3).

Adjust MAX_INDEX to scan deeper into derivation paths.

Use an SSD for faster SQLite queries.

Reduce print frequency to improve throughput.

Split the address database by prefixes for faster lookup.

🔒 Ethical & Legal Notice

This tool demonstrates how BIP39/44/49/84/86 wallets derive Bitcoin addresses,
and how multiprocessing & database lookups can be combined efficiently.

It must not be used to:

Attempt unauthorized recovery of wallet seeds.

Scan or brute-force private keys belonging to real users.

It may be used for:

Security auditing and stress-testing wallet derivation code.

Teaching BIP32/BIP44 derivation principles.

Demonstrating multiprocessing design patterns.

Unauthorized use is illegal and unethical.

🧰 Suggested Improvements

🔧 Add database caching or in-memory indexing for faster lookups

💾 Implement logging with timestamps per worker

🧮 Add progress bar per process using tqdm

🚀 Add CLI configuration with argparse

🧠 Integrate checksum verification and mnemonic entropy testing

🪪 License

MIT License
© 2025 — Author: [Ethicbrudhack]
Free for educational and ethical security research use.

💡 Summary

This project combines:

🔐 HD wallet generation (BIP44/BIP49/BIP84/BIP86)

⚙️ Multiprocessing & concurrency

🗃️ Local database querying

🧠 Mnemonic and seed phrase logic

to demonstrate how wallet derivation works internally —
in a controlled, ethical, and educational environment.

BTC donation address: bc1q4nyq7kr4nwq6zw35pg0zl0k9jmdmtmadlfvqhr
