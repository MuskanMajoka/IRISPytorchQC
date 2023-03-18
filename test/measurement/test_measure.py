import torchquantum as tq

from torchquantum.plugins import op_history2qiskit
from qiskit import Aer, transpile
import numpy as np


def test_measure():

    n_shots = 10000
    qdev = tq.QuantumDevice(n_wires=3, bsz=1, record_op=True)
    qdev.x(wires=2)  # type: ignore
    qdev.x(wires=1)  # type: ignore
    qdev.ry(wires=0, params=0.98)  # type: ignore
    qdev.rx(wires=1, params=1.2)  # type: ignore
    qdev.cnot(wires=[0, 2])  # type: ignore

    tq_counts = tq.measure(qdev, n_shots=n_shots)

    circ = op_history2qiskit(qdev.n_wires, qdev.op_history)
    circ.measure_all()
    simulator = Aer.get_backend("aer_simulator")
    circ = transpile(circ, simulator)
    qiskit_res = simulator.run(circ, shots=n_shots).result()
    qiskit_counts = qiskit_res.get_counts()

    for k, v in tq_counts[0].items():
        # need to reverse the bitstring because qiskit is in little endian
        qiskit_ratio = qiskit_counts.get(k[::-1], 0) / n_shots
        tq_ratio = v / n_shots
        print(k, qiskit_ratio, tq_ratio)
        assert np.isclose(qiskit_ratio, tq_ratio, atol=0.1)

    print("tq.measure test passed")


if __name__ == "__main__":
    import pdb

    pdb.set_trace()
    test_measure()
