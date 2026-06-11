import os

import MySQLdb


def main():
    conn = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "backend"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "sku_db"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        connect_timeout=5,
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM core_product")
    print("products:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM core_order")
    print("orders:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM core_productvariant")
    print("variants:", cur.fetchone()[0])
    cur.execute("SELECT username, is_superuser FROM auth_user WHERE username=%s", ("admin",))
    print("admin:", cur.fetchone())
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
