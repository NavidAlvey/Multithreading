# Navid Alvey
# nxa210002
# CS 4348.003
# OS Project 2

import time
import threading
import queue
import random

printLock = threading.Lock()

def safePrint(string_):
    printLock.acquire() # acquire lock to ensure exclusive print operation
    print(string_)
    printLock.release() # release after printing

# customer class
class Customer(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self) # initialized thread
        self.id = id # assign a unique identifier to each customer
        self.first = random.randint(0, 2) # randomly select first food preference

        # determine if second choice will be made with 50% probability
        if random.random() < 0.5:
            rem = [0, 1, 2] 
            rem.remove(self.first) # remove first choice from options
            self.second = random.choice(rem) # randomly choose from second option
        else:
            self.second = None # no second choice

    def run(self):

        # check if first choice line less than 7 customers
        if line_list[self.first] >= 7:
            if self.second is not None and line_list[self.second] < 7: # if second choice exists and is less than 7
                choice = self.second # have customer choose second choice
            else:
                choice = self.first # have customer choose first choice
        else:
            choice = self.first # go with first choice

        safePrint(f"Customer {self.id} wants to eat {food_list[choice]}") # output the food choice
        if self.second is not None: # if customer has second choice print following
            safePrint(f"Customer {self.id}'s backup choice is {food_list[choice]}")

        # customer chooses random door to enter through
        door = random.randint(0, 1)
        doors_s[door].acquire() # only one at a time
        safePrint(f"Customer {self.id} enters the restaurant through door {door}")
        doors_s[door].release()

        # customer enters line
        tables_sem[choice].acquire()
        line_list[choice] += 1 #add self to line, increment counter
        tables_sem[choice].release()
        safePrint(f"Customer {self.id} waits in line for table {table_list[choice]}") #customer is waiting

        # customer sits at table
        tables_sem[choice].acquire() #try to aquire semaphore, and check if open seating
        while seats_list[choice] >= 4:
            tables_sem[choice].release() #if not open seating then go acquire again
            tables_sem[choice].acquire()

        seats_list[choice] += 1 #once seated
        line_list[choice] -= 1
        safePrint(f"Customer {self.id} is sitting at table {table_list[choice]}")
        tables_sem[choice].release()

        # customer calls waiter when ready
        safePrint(f"Customer {self.id} calls waiter for table {table_list[choice]}")
        waiters_s[choice].release() #release waiter to prompt interaction
        waiters_q[choice].put(self.id) #put customer in queue

        # customer gives order to waiter
        safePrint(f"Customer {self.id} gives order to waiter {choice}") #customer giving order

        order_ready[choice].acquire() #customer waiting to recieve order

        # customer waits then eats
        time.sleep(random.uniform(0.2, 1))
        safePrint(f"Customer {self.id} finished eating")

        tables_sem[choice].acquire()
        seats_list[choice] -= 1 # decrement amount seated, prompt leaving table
        safePrint(f"Customer {self.id} leaving table {table_list[choice]}")
        tables_sem[choice].release()

        #customer pays bill
        ready_to_pay.acquire()
        safePrint(f"Customer {self.id} paying bill")
        ready_to_pay.release()

        # same as before, leave through random door
        door = random.randint(0, 1)
        doors_s[door].acquire()
        safePrint(f"Customer {self.id} leaves through door {door}")
        doors_s[door].release()

        # if its the last customer, no one seated at table and line is empty for table
        if seats_list[choice] == 0 and line_list[choice] == 0:
            final_customer[choice].release() # release waiter to clean table


#  Waiter class
class Waiter(threading.Thread):
    def __init__(self, id, table):
        # initializations
        threading.Thread.__init__(self)
        self.id = id # set id
        self.table = table # set table

    def run(self):

        while True: # keep running interaction
            safePrint(f"Waiter {self.id} waiting for customer at table {table_list[self.table]}") # display table waiter is assigned

            customer_id = waiters_q[self.table].get() # wait for customer in queue
            waiters_s[self.table].acquire() # when called by customer, continue

            # take order from customer
            safePrint(f"Waiter {self.id} takes order from customer {customer_id}") 

            # go to kitchen and wait set time, then leave kitchen
            kitchen_s.acquire()
            safePrint(f"Waiter {self.id} enters kitches")
            time.sleep(random.uniform(0.1, 0.5))
            safePrint(f"Waiter {self.id} leaves kitches")
            kitchen_s.release()

            # waiter waiting for order outisde of kitchen
            safePrint(f"Waiter {self.id} waiting for order")
            time.sleep(random.uniform(0.3, 1))

            # waiter going back into kitchen to retrive order
            kitchen_s.acquire()
            safePrint(f"Waiter {self.id} enters kitches for order")
            time.sleep(random.uniform(0.1, 0.5))
            safePrint(f"Waiter {self.id} leaves kitches with order")
            kitchen_s.release()

            # waiter gives the order to the customer
            safePrint(f"Waiter {self.id} delivers order to customer {customer_id}")
            order_ready[self.table].release() # wait for customer to eat

            if seats_list[self.table] == 1 and line_list[self.table] == 0: # if the last person at table and no one in line
                final_customer[self.table].acquire() # wait for last person to leave
                
                safePrint(f"Waiter {self.id} cleaned table {table_list[self.table]}") # clean table
                safePrint(f"Waiter {self.id} leaves restaurant") # leave
                final_customer[self.table].release() # release for other tables
                break


if __name__ == "__main__":
    # create static vars for table names and food names
    food_list = ['Seafood', 'Steak', 'Pasta']
    table_list = ['A', 'B', 'C']


    # initialize semaphores for each action in simulation
    tables_sem = [threading.Semaphore(1) for _ in range(3)] # 3 tables init to 1
    doors_s = [threading.Semaphore(1) for _ in range(2)] # 2 doors init to 1
    ready_to_pay = threading.Semaphore(1) # 1 person can pay at a time
    kitchen_s = threading.Semaphore(1) # 1 in kitchen at a time
    waiters_s = [threading.Semaphore(0) for _ in range(3)] # 3 waiters
    order_ready = [threading.Semaphore(0) for _ in range(3)] # when customer ready to give order
    final_customer = [threading.Semaphore(0) for _ in range(3)] # when it is the last customer for table
    waiters_q = [queue.Queue() for _ in range(3)] # queue for each waiter

    #  Shared counters
    line_list = [0 for _ in range(3)] # list representing line for each table
    seats_list = [0 for _ in range(3)] # list representing seating at each table

    waiters = [Waiter(i, i) for i in range(3)] # create waiters
    customers = [Customer(i) for i in range(40)] # create customers

    for waiter in waiters: # start waiters
        waiter.start()

    for customer in customers: # start customers
        customer.start()

    # join waiters and customers for interactions
    for waiter in waiters:
        waiter.join()

    for customer in customers:
        customer.join()
