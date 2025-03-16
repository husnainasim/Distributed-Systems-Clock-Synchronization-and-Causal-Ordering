# # causal_ordering.py

class Message:
    def __init__(self, sender, content, vector_clock=None, matrix_clock=None):
        self.sender = sender
        self.content = content
        self.vector_clock = vector_clock  # Used by BSS/SES
        self.matrix_clock = matrix_clock  # Used by Matrix


class ProcessBSS:
    """
    BSS-based causal ordering using vector clocks.
    """
    def __init__(self, pid, total_processes,
                 on_deliver_callback=None,
                 on_clock_update_callback=None):
        self.pid = pid
        self.total = total_processes
        self.vector_clock = [0] * total_processes
        self.buffer = []
        self.delivered = []

        # GUI callbacks
        self.on_deliver_callback = on_deliver_callback
        self.on_clock_update_callback = on_clock_update_callback
        self.update_clock_label()

    def send_message(self, content):
        # Increment local clock
        self.vector_clock[self.pid] += 1
        msg = Message(self.pid, content, vector_clock=self.vector_clock.copy())
        self.update_clock_label()
        return msg

    def receive_message(self, msg):
        if self.can_deliver(msg):
            self.deliver_message(msg)
            self.vector_clock[msg.sender] = msg.vector_clock[msg.sender]
            self.update_clock_label()
            self.check_buffer()
        else:
            self.buffer.append(msg)

    def can_deliver(self, msg):
        s = msg.sender
        # BSS condition: msg.vector_clock[s] == local_clock[s] + 1
        if msg.vector_clock[s] != self.vector_clock[s] + 1:
            return False
        # For all i != s, msg.vector_clock[i] <= local_clock[i]
        for i in range(self.total):
            if i != s and msg.vector_clock[i] > self.vector_clock[i]:
                return False
        return True

    def deliver_message(self, msg):
        # Fire the GUI callback to animate the message
        if self.on_deliver_callback:
            self.on_deliver_callback(msg.sender, self.pid, msg.content)
        # For console/log
        print(f"[BSS] Process {self.pid} delivered from {msg.sender}: {msg.content}")
        self.delivered.append(msg)

    def check_buffer(self):
        delivered_something = True
        while delivered_something:
            delivered_something = False
            for msg in self.buffer.copy():
                if self.can_deliver(msg):
                    self.deliver_message(msg)
                    self.vector_clock[msg.sender] = msg.vector_clock[msg.sender]
                    self.update_clock_label()
                    self.buffer.remove(msg)
                    delivered_something = True

    def update_clock_label(self):
        if self.on_clock_update_callback:
            clock_str = "(" + ",".join(map(str, self.vector_clock)) + ")"
            self.on_clock_update_callback(self.pid, clock_str)


class ProcessSES:
    """
    SES-based causal ordering.
    For simplicity, we use the same vector-clock approach as BSS,
    but you can add any special SES logic you want.
    """
    def __init__(self, pid, total_processes,
                 on_deliver_callback=None,
                 on_clock_update_callback=None):
        self.pid = pid
        self.total = total_processes
        self.vector_clock = [0] * total_processes
        self.buffer = []
        self.delivered = []

        self.on_deliver_callback = on_deliver_callback
        self.on_clock_update_callback = on_clock_update_callback
        self.update_clock_label()

    def send_message(self, content):
        self.vector_clock[self.pid] += 1
        msg = Message(self.pid, content, vector_clock=self.vector_clock.copy())
        self.update_clock_label()
        return msg

    def receive_message(self, msg):
        if self.can_deliver(msg):
            self.deliver_message(msg)
            self.vector_clock[msg.sender] = msg.vector_clock[msg.sender]
            self.update_clock_label()
            self.check_buffer()
        else:
            self.buffer.append(msg)

    def can_deliver(self, msg):
        s = msg.sender
        if msg.vector_clock[s] != self.vector_clock[s] + 1:
            return False
        for i in range(self.total):
            if i != s and msg.vector_clock[i] > self.vector_clock[i]:
                return False
        return True

    def deliver_message(self, msg):
        if self.on_deliver_callback:
            self.on_deliver_callback(msg.sender, self.pid, msg.content)
        print(f"[SES] Process {self.pid} delivered from {msg.sender}: {msg.content}")
        self.delivered.append(msg)

    def check_buffer(self):
        delivered_something = True
        while delivered_something:
            delivered_something = False
            for msg in self.buffer.copy():
                if self.can_deliver(msg):
                    self.deliver_message(msg)
                    self.vector_clock[msg.sender] = msg.vector_clock[msg.sender]
                    self.update_clock_label()
                    self.buffer.remove(msg)
                    delivered_something = True

    def update_clock_label(self):
        if self.on_clock_update_callback:
            clock_str = "(" + ",".join(map(str, self.vector_clock)) + ")"
            self.on_clock_update_callback(self.pid, clock_str)


class ProcessMatrix:
    """
    Matrix Clock-based causal ordering.
    Each process maintains a matrix clock.
    """
    def __init__(self, pid, total_processes,
                 on_deliver_callback=None,
                 on_clock_update_callback=None):
        self.pid = pid
        self.total = total_processes
        self.vector_clock = [0] * total_processes  # used for local increments
        # Initialize matrix_clock: each process knows only its own vector initially.
        self.matrix_clock = [[0]*total_processes for _ in range(total_processes)]
        self.buffer = []
        self.delivered = []

        self.on_deliver_callback = on_deliver_callback
        self.on_clock_update_callback = on_clock_update_callback
        self.update_clock_label()

    def send_message(self, content):
        # Update local vector clock
        self.vector_clock[self.pid] += 1
        # Copy into local row of matrix_clock
        self.matrix_clock[self.pid] = self.vector_clock.copy()

        # Attach a deep copy of the matrix
        import copy
        msg_matrix = copy.deepcopy(self.matrix_clock)

        msg = Message(self.pid, content, matrix_clock=msg_matrix)
        self.update_clock_label()
        return msg

    def receive_message(self, msg):
        if self.can_deliver(msg):
            self.deliver_message(msg)
            # On receive, increment our own clock before merging (as in the algorithm example)
            self.matrix_clock[self.pid][self.pid] += 1
            # Merge sender's information into our own row only
            s = msg.sender
            for j in range(self.total):
                self.matrix_clock[self.pid][j] = max(self.matrix_clock[self.pid][j], msg.matrix_clock[s][j])
            self.update_clock_label()
            self.check_buffer()
        else:
            self.buffer.append(msg)

    def can_deliver(self, msg):
        s = msg.sender
        # Delivery condition for matrix clocks:
        # The sender's own clock in the message must be exactly one more than our known value.
        if msg.matrix_clock[s][s] != self.matrix_clock[s][s] + 1:
            return False
        # And for all other indices in sender's row, the message's values must be <= our known values.
        for i in range(self.total):
            if i != s and msg.matrix_clock[s][i] > self.matrix_clock[s][i]:
                return False
        return True

    def deliver_message(self, msg):
        if self.on_deliver_callback:
            self.on_deliver_callback(msg.sender, self.pid, msg.content)
        print(f"[Matrix] Process {self.pid} delivered from {msg.sender}: {msg.content}")
        self.delivered.append(msg)

    def check_buffer(self):
        delivered_something = True
        while delivered_something:
            delivered_something = False
            for msg in self.buffer.copy():
                if self.can_deliver(msg):
                    self.deliver_message(msg)
                    # On delivery, increment our own clock and merge sender's row.
                    self.matrix_clock[self.pid][self.pid] += 1
                    s = msg.sender
                    for j in range(self.total):
                        self.matrix_clock[self.pid][j] = max(self.matrix_clock[self.pid][j], msg.matrix_clock[s][j])
                    self.update_clock_label()
                    self.buffer.remove(msg)
                    delivered_something = True

    def update_clock_label(self):
        """
        For demonstration, show only the local row of the matrix,
        i.e., matrix_clock[pid].
        """
        if self.on_clock_update_callback:
            row_str = "(" + ",".join(map(str, self.matrix_clock[self.pid])) + ")"
            self.on_clock_update_callback(self.pid, row_str)


# -------------------------------------
# Simulation Functions
# -------------------------------------

def simulate_BSS(processes):
    """
    Example simulation for BSS.
    `processes` is a list of ProcessBSS objects.
    We show how to do an out-of-order delivery scenario.
    """
    # Create messages
    m1 = processes[0].send_message("Message A from P0")
    m2 = processes[1].send_message("Message B from P1")
    m3 = processes[2].send_message("Message C from P2")

    # Deliver them to P1 in out-of-order order.
    p1 = processes[1]
    p1.receive_message(m1)  # Should deliver immediately.
    p1.receive_message(m3)  # Might be buffered.
    p1.receive_message(m2)  # Triggers p1 to deliver buffered messages.


def simulate_SES(processes):
    """
    Example simulation for SES.
    """
    m1 = processes[0].send_message("Message A from P0")
    m2 = processes[1].send_message("Message B from P1")
    m3 = processes[2].send_message("Message C from P2")

    # Deliver them to P2 in some order.
    p2 = processes[2]
    p2.receive_message(m2)
    p2.receive_message(m1)
    p2.receive_message(m3)


def simulate_Matrix(processes):
    """
    Example simulation for Matrix Clock.
    Note: we now deliver messages to process 1 (instead of process 0) so that
    a process is not receiving its own message.
    """
    m1 = processes[0].send_message("Message A from P0")
    m2 = processes[1].send_message("Message B from P1")
    m3 = processes[2].send_message("Message C from P2")

    # Deliver messages to process 1 in out-of-order order.
    p1 = processes[1]
    p1.receive_message(m2)
    p1.receive_message(m3)
    p1.receive_message(m1)
