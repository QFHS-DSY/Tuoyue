import os

import MySQLdb


def _quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main():
    root_user = os.getenv("MYSQL_ROOT_USER", "root")
    root_password = os.getenv("MYSQL_ROOT_PASSWORD", "")
    app_user = os.getenv("MYSQL_APP_USER", os.getenv("MYSQL_USER", "backend"))
    app_password = os.getenv("MYSQL_APP_PASSWORD", os.getenv("MYSQL_PASSWORD", ""))
    database = os.getenv("MYSQL_DATABASE", "sku_db")
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = int(os.getenv("MYSQL_PORT", "3306"))

    if not app_password:
        raise SystemExit("MYSQL_APP_PASSWORD or MYSQL_PASSWORD is required")

    conn = MySQLdb.connect(host=host, user=root_user, passwd=root_password, database="mysql", port=port)
    cur = conn.cursor()
    cur.execute(f"CREATE USER IF NOT EXISTS {_quote(app_user)}@'%' IDENTIFIED BY {_quote(app_password)}")
    cur.execute(f"GRANT ALL PRIVILEGES ON `{database}`.* TO {_quote(app_user)}@'%'")
    cur.execute("FLUSH PRIVILEGES")
    cur.close()
    conn.close()
    print(f"User {app_user} created successfully")


if __name__ == "__main__":
    main()
