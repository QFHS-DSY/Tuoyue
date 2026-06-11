import MySQLdb
conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root_dev_only', database='mysql', port=3306)
cur = conn.cursor()
cur.execute("CREATE USER IF NOT EXISTS 'admin_erp'@'localhost' IDENTIFIED BY 'Bzh200257.'")
cur.execute("GRANT ALL PRIVILEGES ON sku_db.* TO 'admin_erp'@'localhost'")
cur.execute("FLUSH PRIVILEGES")
cur.close()
conn.close()
print("User admin_erp created successfully")
