import psycopg2
import psycopg2.extras

con= psycopg2.connect(host = "localhost" , 
                      database ="TunisiaCD" , 
                      user = "postgres" , 
                      password= "oussama.bh")

cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)



def commit(): 
    con.commit()