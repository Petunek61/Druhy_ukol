import unittest
import mysql.connector
from mysql.connector import Error

TEST_DB = "ukoly_test_db"

# 🏗️ Vytvoření testovací databáze (pokud neexistuje)
def vytvor_testovaci_databazi():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="19611966"
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;")
        conn.commit()
        conn.close()
        print("✅ Testovací databáze připravena.")
    except Error as e:
        print(f"Chyba při vytváření testovací databáze: {e}")

# 🧹 Odstranění testovací databáze po skončení testů
def smaz_testovaci_databazi():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="19611966"
        )
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB};")
        conn.commit()
        conn.close()
        print("🧹 Testovací databáze byla odstraněna.")
    except Error as e:
        print(f"Chyba při mazání testovací databáze: {e}")

# 🔌 Připojení k testovací databázi
def pripojeni_test_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="19611966",
        database=TEST_DB
    )

# 🧱 Vytvoření tabulky `ukoly` v testovací databázi
def nastav_testovaci_tabulku(conn):
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL CHECK (nazev <> ''),
            popis TEXT NOT NULL CHECK (popis <> ''),
            stav ENUM('nezahájeno', 'hotovo', 'probíhá') DEFAULT 'nezahájeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

# 🧪 Testovací třída
class TestUkoly(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        vytvor_testovaci_databazi()
        cls.conn = pripojeni_test_db()
        nastav_testovaci_tabulku(cls.conn)

    def setUp(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM ukoly")
        self.conn.commit()

    # ✅ Přidání úkolu – pozitivní
    def test_pridat_ukol_validni(self):
        self.cursor.execute("""
            INSERT INTO ukoly (nazev, popis, stav)
            VALUES (%s, %s, %s)
        """, ("Testovací úkol", "Popis", "nezahájeno"))
        self.conn.commit()
        self.cursor.execute("SELECT COUNT(*) FROM ukoly WHERE nazev = 'Testovací úkol'")
        self.assertEqual(self.cursor.fetchone()[0], 1)

    # ❌ Přidání úkolu – negativní (prázdný popis)
    def test_pridat_ukol_prazdny_popis(self):
        with self.assertRaises(Error):
            self.cursor.execute("""
                INSERT INTO ukoly (nazev, popis)
                VALUES (%s, %s)
            """, ("Něco", ""))
            self.conn.commit()

    # ✅ Aktualizace úkolu – pozitivní
    def test_aktualizovat_ukol_validni(self):
        self.cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Aktualizace", "Test"))
        self.conn.commit()
        self.cursor.execute("SELECT id FROM ukoly WHERE nazev = 'Aktualizace'")
        ukol_id = self.cursor.fetchone()[0]
        self.cursor.execute("UPDATE ukoly SET stav = 'hotovo' WHERE id = %s", (ukol_id,))
        self.conn.commit()
        self.cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (ukol_id,))
        self.assertEqual(self.cursor.fetchone()[0], 'hotovo')

    # ❌ Aktualizace úkolu – negativní (neexistující ID)
    def test_aktualizovat_ukol_neexistujici(self):
        self.cursor.execute("UPDATE ukoly SET stav = 'hotovo' WHERE id = -1")
        self.conn.commit()
        self.assertEqual(self.cursor.rowcount, 0)

    # ✅ Odstranění úkolu – pozitivní
    def test_odstranit_ukol_validni(self):
        self.cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Smazat", "Úkol"))
        self.conn.commit()
        self.cursor.execute("SELECT id FROM ukoly WHERE nazev = 'Smazat'")
        ukol_id = self.cursor.fetchone()[0]
        self.cursor.execute("DELETE FROM ukoly WHERE id = %s", (ukol_id,))
        self.conn.commit()
        self.cursor.execute("SELECT COUNT(*) FROM ukoly WHERE id = %s", (ukol_id,))
        self.assertEqual(self.cursor.fetchone()[0], 0)

    # ❌ Odstranění úkolu – negativní (neexistující ID)
    def test_odstranit_ukol_neexistujici(self):
        self.cursor.execute("DELETE FROM ukoly WHERE id = -999")
        self.conn.commit()
        self.assertEqual(self.cursor.rowcount, 0)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        smaz_testovaci_databazi()
        print("✅ Testy dokončeny a databáze odstraněna.")


# ▶️ Spuštění testů
if __name__ == "__main__":
    unittest.main()