
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
import os
import socket
import threading
import time
import sys

# ==========================================
# KRYŠTOF FOOD - PRENOSNY SERVER
# ==========================================

SLOZKA = os.path.dirname(os.path.abspath(__file__))
os.chdir(SLOZKA)

SOUBOR_OBJEDNAVKY = os.path.join(SLOZKA, "objednavky.json")
SOUBOR_CISLA = os.path.join(SLOZKA, "cislo_objednavky.json")

ZAMEK = threading.Lock()


# ==========================================
# STARTOVACI ANIMACE
# ==========================================

def startovani():
    ukoly = [
        "Inicializace systému",
        "Kontrola souborů",
        "Načítání objednávek",
        "Příprava kuchyně",
        "Příprava výdeje",
        "Připojení serveru",
        "Dokončení spuštění"
    ]

    for i, ukol in enumerate(ukoly):
        os.system("cls" if os.name == "nt" else "clear")

        print()
        print("=" * 58)
        print("                 KRYŠTOF FOOD")
        print("              PROFESIONALNI SYSTEM")
        print("=" * 58)
        print()
        print("             STARTUJI SYSTEM...")
        print()
        print(f"       [{i + 1}/7] {ukol}...")
        print()

        hotovo = "#" * ((i + 1) * 3)
        print(f"       [{hotovo:<21}]")

        time.sleep(1.5)

    os.system("cls" if os.name == "nt" else "clear")

    print()
    print("=" * 58)
    print("             KRYŠTOF FOOD")
    print("          SYSTEM JE PRIPRAVEN!")
    print("=" * 58)

    time.sleep(1)


# ==========================================
# VYPINACI ANIMACE
# ==========================================

def vypinani():
    ukoly = [
        "Ukončování objednávkového systému",
        "Ukládání dat",
        "Ukončování kuchyně",
        "Ukončování výdeje",
        "Odpojování zařízení",
        "Uzavírání serveru",
        "Dokončení vypínání"
    ]

    for i, ukol in enumerate(ukoly):
        os.system("cls" if os.name == "nt" else "clear")

        print()
        print("=" * 58)
        print("                 KRYŠTOF FOOD")
        print("              VYPINANI SERVERU")
        print("=" * 58)
        print()
        print("             PROSIM CEKEJ...")
        print()
        print(f"       [{i + 1}/7] {ukol}...")
        print()

        hotovo = "#" * ((i + 1) * 3)
        print(f"       [{hotovo:<21}]")

        time.sleep(12 / 7)

    os.system("cls" if os.name == "nt" else "clear")

    print()
    print("=" * 58)
    print("                 KRYŠTOF FOOD")
    print()
    print("             SERVER BYL VYPNUT")
    print("=" * 58)
    print()
    print("             DEKUJEME ZA POUZIVANI")
    print()
    time.sleep(1)


# ==========================================
# OBJEDNAVKY
# ==========================================

def nacti_objednavky():
    try:
        with open(SOUBOR_OBJEDNAVKY, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def uloz_objednavky(data):
    with open(SOUBOR_OBJEDNAVKY, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def nacti_cislo():
    try:
        with open(SOUBOR_CISLA, "r", encoding="utf-8") as f:
            return int(json.load(f))
    except (FileNotFoundError, ValueError, TypeError, json.JSONDecodeError):
        objednavky = nacti_objednavky()
        nejvyssi = max(
            (int(o.get("number", 100)) for o in objednavky),
            default=100
        )
        return max(100, nejvyssi)


def uloz_cislo(cislo):
    with open(SOUBOR_CISLA, "w", encoding="utf-8") as f:
        json.dump(cislo, f)


# ==========================================
# WEB SERVER
# ==========================================

class Server(SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        print("[KRYŠTOF FOOD]", format % args)

    def do_GET(self):
        if self.path == "/api/orders":
            with ZAMEK:
                data = nacti_objednavky()

            vystup = json.dumps(data, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(vystup)))
            self.end_headers()
            self.wfile.write(vystup)
            return

        super().do_GET()

    def do_POST(self):
        if self.path == "/api/next-number":
            with ZAMEK:
                cislo = nacti_cislo() + 1
                uloz_cislo(cislo)

            self.odesli_json({"number": cislo})
            return

        if self.path == "/api/orders":
            try:
                delka = int(self.headers.get("Content-Length", 0))
                data = json.loads(
                    self.rfile.read(delka).decode("utf-8")
                )

                if not isinstance(data, list):
                    self.odesli_json({"error": "Neplatná data"}, 400)
                    return

                with ZAMEK:
                    uloz_objednavky(data)

                    nejvyssi = max(
                        (int(o.get("number", 100)) for o in data),
                        default=100
                    )

                    uloz_cislo(max(nacti_cislo(), nejvyssi))

                self.odesli_json({"success": True})

            except (ValueError, TypeError, json.JSONDecodeError):
                self.odesli_json({"error": "Chybná data"}, 400)

            return

        self.odesli_json({"error": "Neznámý požadavek"}, 404)

    def odesli_json(self, data, kod=200):
        vystup = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(vystup)))
        self.end_headers()
        self.wfile.write(vystup)


# ==========================================
# IP ADRESA POCITACE
# ==========================================

def zjisti_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


# ==========================================
# HLAVNI PROGRAM
# ==========================================

if __name__ == "__main__":

    server = None

    try:
        startovani()

        if not os.path.exists(SOUBOR_OBJEDNAVKY):
            uloz_objednavky([])

        if not os.path.exists(SOUBOR_CISLA):
            uloz_cislo(nacti_cislo())

        ip = zjisti_ip()

        server = ThreadingHTTPServer(
            ("0.0.0.0", 8765),
            Server
        )

        os.system("cls" if os.name == "nt" else "clear")

        print()
        print("=" * 62)
        print("                    KRYŠTOF FOOD")
        print("                 PROFESIONALNI SERVER")
        print("=" * 62)

        print()
        print("              SERVER BYL USPESNE SPUSTEN")
        print()
        print("-" * 62)
        print("             IP ADRESA TOHOTO POCITACE")
        print()
        print(f"                    {ip}")
        print()
        print("-" * 62)

        print()
        print(" OBJEDNAVKY:")
        print(f" http://{ip}:8765/objednavka.html")

        print()
        print(" KUCHYNE:")
        print(f" http://{ip}:8765/kuchyn.html")

        print()
        print(" VYDEJ:")
        print(f" http://{ip}:8765/vydej.html")

        print()
        print("=" * 62)
        print(" DATA SE UKLADAJI NA FLASHKU.")
        print(" SERVER BEZI - NEZAVIREJ TOTO OKNO.")
        print(" PRO VYPNUTI STISKNI CTRL + C")
        print("=" * 62)

        server.serve_forever()

    except KeyboardInterrupt:
        if server:
            server.shutdown()
            server.server_close()

        vypinani()

    except OSError as e:
        print()
        print("CHYBA SERVERU:", e)
        input("Stiskni ENTER pro ukonceni...")


