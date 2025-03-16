# Distributed Systems Causal Ordering Algorithms Implementation

This repository contains Python implementations of three fundamental causal ordering algorithms used in distributed systems:

- BSS (Birman-Schiper-Stephenson) Algorithm
- SES (Schiper-Eggli-Sandoz) Algorithm
- Matrix Clock Algorithm

## Overview

The project demonstrates how different distributed systems maintain causal ordering of messages in an asynchronous environment. Each algorithm uses a different approach to ensure that messages are delivered in a causally consistent order, even in the presence of network delays and out-of-order message delivery.

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