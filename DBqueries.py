import psycopg2

conn = None


def connect_to_db():
    try:
        global conn
        conn = psycopg2.connect("dbname='d2h2b8ktkdsumv'"
                                " user='wewtulwwvdturz' "
                                "host='ec2-23-21-189-181.compute-1.amazonaws.com' "
                                "password='09c1c710a5873351239fcb5002e53085ea683cfc29f40f23ed5ba9bc0e03770f'")
    except:
        print("I am unable to connect to the database")


def select_user(userd_id):
    cur = conn.cursor()
    cur.execute("select * from users where user_id = " + str(userd_id) + ";")
    user = cur.fetchone()
    cur.close()
    return user


def insert_user(user_id, lat, long):
    cur = conn.cursor()
    cur.execute("insert into users values(%s,%s,%s)", (user_id, lat, long))
    conn.commit()
    cur.close()


def update_user(user_id, lat, long):
    cur = conn.cursor()
    cur.execute("update users set lat = %s, long = %s where user_id = %s", (lat, long, user_id))
    conn.commit()
    cur.close()


def select_emoji(emoji):
    cur = conn.cursor()
    cur.execute("select description from emojis where emoji = %s", (emoji))
    emoji = cur.fetchone()
    cur.close()
    return emoji


def find_cuisine_by_dish(dish):
    dish = dish.lower()
    cur = conn.cursor()
    cur.execute(
        "select c.name_cus from cuisine c inner join dish d on(c.id_cus = d.id_cus_d) where lower(d.name_dish) LIKE '%" + str(
            dish) + "%';")
    cuisine = cur.fetchone()
    cur.close
    return cuisine[0] + " кухня"


def close_connection():
    conn.close()
