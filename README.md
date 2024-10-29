# Restaurant Simulation
The RestaurantSimulation.py script simulates a restaurant environment where multiple customers interact, each with unique food preferences.
The program leverages multithreading to represent customers and their activities concurrently, ensuring efficient handling of customer requests and preferences.
This simulation is designed to model realistic restaurant behavior, such as customer choice variability, waiting for orders, and dealing with limited food availability.

## Description
### Multithreading
- Each customer is represented by a separate thread, allowing concurrent actions and simulating real-time customer interactions.

### Thread-Safe Printing
- To handle the concurrency of customer threads, a print lock is implemented, ensuring outputs do not overlap or interleave, providing a cleaner and more readable console output.

### Randomized Customer Preferences
- Each customer is initialized with a randomly assigned food preference. Additionally, a customer may have a secondary preference, chosen based on a probability, adding a layer of realism to the simulation.

## Functionality
### Customer Creation
Each customer is represented as an instance of the Customer class, which inherits from threading.Thread. The constructor initializes each customer with:
- A unique identifier
- A random food preference
- A potential secondary preference chosen with a 50% probability

### Running the Simulation
Each customer (thread) checks for the availability of their preferred food. If unavailable, they either wait or switch to their secondary preference if applicable.

### Thread Safety with safePrint:
To prevent overlapping outputs from different threads, the safePrint function is used to acquire and release a lock for each print statement, ensuring synchronized console output.
