import booking_database
import time

def start():
    while(True):
        for booking in booking_database.get_all_entries():
            print(booking)
        time.sleep(60)