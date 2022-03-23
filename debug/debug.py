from decouple import config
import psycopg2


# CONNECT TO DB #
database = {
    "host": config("DB_HOST", cast=str),
    "database": config("DB_DATABASE", cast=str),
    "user": config("DB_USER", cast=str),
    "password": config("DB_PASSWORD", cast=str),
    "port": config("DB_PORT", cast=int),
    "min_size": config("DB_MIN_SIZE", cast=int, default=1),
    "max_size": config("DB_MAX_SIZE", cast=int, default=5)
}

def faction_keys(faction_id):
    db_cred = {
        "dbname": database.get("database"),
        "user": database.get("user"),
        "password": database.get("password"),
        "host": database.get("host"),
        "port": database.get("port")
    }
    con = psycopg2.connect(**db_cred)

    # get bot
    cur = con.cursor()
    cur.execute(f'SELECT id FROM player_player WHERE "factionAA" = True and "factionId" = {faction_id};')
    keys = []
    for i in cur.fetchall():
        cur.execute(f'SELECT value FROM player_key WHERE player_id = {i[0]};')
        keys.append(cur.fetchone())

    cur.close()

    return [_[0] for _ in keys if _]

def player_key(player_id):
    db_cred = {
        "dbname": database.get("database"),
        "user": database.get("user"),
        "password": database.get("password"),
        "host": database.get("host"),
        "port": database.get("port")
    }
    con = psycopg2.connect(**db_cred)

    # get bot
    cur = con.cursor()
    cur.execute(f'SELECT value FROM player_key WHERE "tId" = {player_id};')
    key = cur.fetchone()
    cur.close()

    if key:
        return key[0]
    else:
        return None
