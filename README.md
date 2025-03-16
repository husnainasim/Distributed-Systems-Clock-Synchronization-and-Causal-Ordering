# Distributed Systems Causal Ordering Algorithms Implementation

This repository contains Python implementations of three fundamental causal ordering algorithms used in distributed systems:

- BSS (Birman-Schiper-Stephenson) Algorithm
- SES (Schiper-Eggli-Sandoz) Algorithm
- Matrix Clock Algorithm

## Overview

The project demonstrates how different distributed systems maintain causal ordering of messages in an asynchronous environment. Each algorithm uses a different approach to ensure that messages are delivered in a causally consistent order, even in the presence of network delays and out-of-order message delivery.

## Project Setup

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/distributed-causal-ordering.git
cd distributed-causal-ordering
```

2. Ensure you have Python 3.6 or higher installed:
```bash
python --version
```

3. No additional dependencies are required, but if you want to use the GUI visualization:
```bash
pip install tkinter  # Usually comes pre-installed with Python
```

4. Run the main simulation:
```bash
python main.py
```

## Project Structure

```
distributed-causal-ordering/
│
├── causal_ordering.py   # Main implementation of all algorithms
├── main.py             # Entry point and simulation runner
├── gui.py             # GUI visualization (optional)
├── README.md          # This file
└── LICENSE            # MIT License
```

## Algorithms Implemented

### 1. BSS (Birman-Schiper-Stephenson) Algorithm
- Uses vector clocks to track causal dependencies
- Each process maintains a vector clock that tracks the latest known event count from each process
- Messages carry vector timestamps
- Delivery conditions ensure causal ordering:
  - Message's sender clock should be exactly one more than receiver's known sender clock
  - All other vector components should not exceed receiver's knowledge

### 2. SES (Schiper-Eggli-Sandoz) Algorithm
- Explicitly tracks message dependencies
- Each message carries its direct causal dependencies
- Simpler delivery rule: deliver only when all dependencies are satisfied
- More efficient in terms of message size when causal dependencies are sparse

### 3. Matrix Clock Algorithm
- Uses a matrix of clocks to track both direct and indirect causal relationships
- Each process maintains an n×n matrix (where n is the number of processes)
- Each row represents a process's view of the system
- Provides complete causal history but with higher space complexity

## Example Inputs and Outputs

### 1. BSS Algorithm Example

Input:
```python
# Create three processes
processes = [ProcessBSS(i, 3) for i in range(3)]

# Process 0 sends a message
m1 = processes[0].send_message("Hello from P0")
```

Output:
```
[BSS] Process 0 vector clock: (1,0,0)
[BSS] Process 1 received message from P0: "Hello from P0"
[BSS] Process 1 vector clock updated to: (1,1,0)
```

### 2. SES Algorithm Example

Input:
```python
# Create three processes
processes = [ProcessSES(i, 3) for i in range(3)]

# Process 0 sends two messages
m1 = processes[0].send_message("First message")
m2 = processes[0].send_message("Second message")

# Process 1 receives them out of order
processes[1].receive_message(m2)
processes[1].receive_message(m1)
```

Output:
```
[SES] Message m2 buffered: waiting for dependencies
[SES] Delivered message m1: "First message"
[SES] Dependencies satisfied, delivering m2: "Second message"
```

### 3. Matrix Clock Example

Input:
```python
# Create three processes
processes = [ProcessMatrix(i, 3) for i in range(3)]

# Simulate a message chain
m1 = processes[0].send_message("Start")
processes[1].receive_message(m1)
m2 = processes[1].send_message("Middle")
processes[2].receive_message(m2)
```

Output:
```
[Matrix] P0 matrix clock:
[1,0,0]
[0,0,0]
[0,0,0]

[Matrix] P1 matrix clock after receiving m1:
[1,0,0]
[1,1,0]
[0,0,0]

[Matrix] P2 matrix clock after receiving m2:
[1,0,0]
[1,2,0]
[1,2,1]
```

## Sample Execution Flow

Here's a complete example showing how messages are ordered causally:

```python
from causal_ordering import ProcessBSS

# Create three processes
processes = [ProcessBSS(i, 3) for i in range(3)]

# P0 sends message to P1 and P2
m1 = processes[0].send_message("First")
processes[1].receive_message(m1)
processes[2].receive_message(m1)

# P1 sends message to P2
m2 = processes[1].send_message("Second")

# P2 receives m2 before m1 (out of order)
processes[2].receive_message(m2)  # Will be buffered
processes[2].receive_message(m1)  # Will be delivered and trigger m2 delivery
```

Expected output:
```
[BSS] P0 sent message "First" with clock (1,0,0)
[BSS] P1 delivered message "First" with clock (1,1,0)
[BSS] P1 sent message "Second" with clock (1,2,0)
[BSS] P2: Buffering message "Second" - waiting for message "First"
[BSS] P2 delivered message "First" with clock (1,0,1)
[BSS] P2 delivered buffered message "Second" with clock (1,2,1)
```

## Visualization

If you're using the GUI version, you'll see a visual representation of:
- Process states and their vector/matrix clocks
- Message transmission between processes
- Message buffering and delivery events

[You can add screenshots of your GUI here]

## Common Issues and Solutions

1. **Messages not being delivered**
   - Check if all causal dependencies are satisfied
   - Verify that vector/matrix clocks are being updated correctly

2. **Incorrect message ordering**
   - Ensure the delivery conditions in each algorithm are properly implemented
   - Verify that the buffer checking mechanism is working

3. **GUI not showing**
   - Make sure tkinter is installed
   - Check if the GUI thread is properly initialized

## Running Tests

To run the built-in tests:
```bash
python -m unittest tests/test_causal_ordering.py
```

## Implementation Details

The code is structured into three main classes:
- `ProcessBSS`: Implementation of BSS algorithm
- `ProcessSES`: Implementation of SES algorithm
- `ProcessMatrix`: Implementation of Matrix Clock algorithm

Each class provides:
- Message sending functionality
- Message receiving and delivery logic
- Buffer management for out-of-order messages
- Causal dependency checking
- Vector/Matrix clock maintenance

## Usage Example

```python
# Create processes (e.g., for BSS algorithm)
processes = [ProcessBSS(i, 3) for i in range(3)]

# Send messages
m1 = processes[0].send_message("Message A from P0")
m2 = processes[1].send_message("Message B from P1")
m3 = processes[2].send_message("Message C from P2")

# Deliver messages (possibly out of order)
p1 = processes[1]
p1.receive_message(m1)  # Will be delivered
p1.receive_message(m3)  # May be buffered
p1.receive_message(m2)  # May trigger delivery of buffered messages
```

## Features

- Clean, object-oriented implementation
- Support for GUI callbacks to visualize message delivery
- Buffer management for out-of-order messages
- Comprehensive simulation functions for testing
- Clock visualization through string representation

## Requirements

- Python 3.6 or higher
- No external dependencies required

## Running the Simulations

The repository includes simulation functions for each algorithm:

```python
# Import the required classes
from causal_ordering import ProcessBSS, ProcessSES, ProcessMatrix

# Run BSS simulation
processes = [ProcessBSS(i, 3) for i in range(3)]
simulate_BSS(processes)

# Run SES simulation
processes = [ProcessSES(i, 3) for i in range(3)]
simulate_SES(processes)

# Run Matrix Clock simulation
processes = [ProcessMatrix(i, 3) for i in range(3)]
simulate_Matrix(processes)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

1. Birman, K. P., Schiper, A., & Stephenson, P. (1991). Lightweight causal and atomic group multicast
2. Schiper, A., Eggli, J., & Sandoz, A. (1989). A new algorithm to implement causal ordering
3. Weihl, W. E. (1989). Local atomicity properties: Modular concurrency control for abstract data types

## Author

[Your Name]

## Acknowledgments

- Thanks to the original authors of these algorithms
- Special thanks to the distributed systems research community 