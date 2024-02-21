"""
MIT License

Copyright (c) 2020-present TorchQuantum Authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# test the torchquantum.functional against the IBM Qiskit
import argparse
import pdb
import torchquantum as tq
import numpy as np

import qiskit.circuit.library.standard_gates as qiskit_gate
from qiskit.quantum_info import DensityMatrix as qiskitDensity

from unittest import TestCase

from random import randrange

import qiskit.circuit.library as qiskit_library
from qiskit.quantum_info import Operator

RND_TIMES = 100

single_gate_list = [
    {"qiskit": qiskit_gate.HGate, "tq": tq.h, "name": "Hadamard"},
    {"qiskit": qiskit_gate.XGate, "tq": tq.x, "name": "x"},
    # {"qiskit": qiskit_gate.YGate, "tq": tq.y, "name": "y"},
    {"qiskit": qiskit_gate.ZGate, "tq": tq.z, "name": "z"},
    {"qiskit": qiskit_gate.SGate, "tq": tq.S, "name": "S"},
    {"qiskit": qiskit_gate.TGate, "tq": tq.T, "name": "T"},
    # {"qiskit": qiskit_gate.SXGate, "tq": tq.SX, "name": "SX"},
    {"qiskit": qiskit_gate.SdgGate, "tq": tq.SDG, "name": "SDG"},
    {"qiskit": qiskit_gate.TdgGate, "tq": tq.TDG, "name": "TDG"}
]

single_param_gate_list = [

]

two_qubit_gate_list = [
    {"qiskit": qiskit_gate.CXGate, "tq": tq.CNOT, "name": "CNOT"},
    {"qiskit": qiskit_gate.CYGate, "tq": tq.CY, "name": "CY"},
    {"qiskit": qiskit_gate.CZGate, "tq": tq.CZ, "name": "CZ"},
    {"qiskit": qiskit_gate.SwapGate, "tq": tq.SWAP, "name": "SWAP"}
]

two_qubit_param_gate_list = [

]

three_qubit_gate_list = [
    {"qiskit": qiskit_gate.CCXGate, "tq": tq.Toffoli, "name": "Toffoli"},
    {"qiskit": qiskit_gate.CSwapGate, "tq": tq.CSWAP, "name": "CSWAP"}
]

three_qubit_param_gate_list = [
]

pair_list = [
    {"qiskit": qiskit_gate.HGate, "tq": tq.Hadamard},
    {"qiskit": None, "tq": tq.SHadamard},
    {"qiskit": qiskit_gate.XGate, "tq": tq.PauliX},
    {"qiskit": qiskit_gate.YGate, "tq": tq.PauliY},
    {"qiskit": qiskit_gate.ZGate, "tq": tq.PauliZ},
    {"qiskit": qiskit_gate.SGate, "tq": tq.S},
    {"qiskit": qiskit_gate.TGate, "tq": tq.T},
    {"qiskit": qiskit_gate.SXGate, "tq": tq.SX},
    {"qiskit": qiskit_gate.CXGate, "tq": tq.CNOT},
    {"qiskit": qiskit_gate.CYGate, "tq": tq.CY},
    {"qiskit": qiskit_gate.CZGate, "tq": tq.CZ},
    {"qiskit": qiskit_gate.RXGate, "tq": tq.RX},
    {"qiskit": qiskit_gate.RYGate, "tq": tq.RY},
    {"qiskit": qiskit_gate.RZGate, "tq": tq.RZ},
    {"qiskit": qiskit_gate.RXXGate, "tq": tq.RXX},
    {"qiskit": qiskit_gate.RYYGate, "tq": tq.RYY},
    {"qiskit": qiskit_gate.RZZGate, "tq": tq.RZZ},
    {"qiskit": qiskit_gate.RZXGate, "tq": tq.RZX},
    {"qiskit": qiskit_gate.SwapGate, "tq": tq.SWAP},
    # {'qiskit': qiskit_gate.?, 'tq': tq.SSWAP},
    {"qiskit": qiskit_gate.CSwapGate, "tq": tq.CSWAP},
    {"qiskit": qiskit_gate.CCXGate, "tq": tq.Toffoli},
    {"qiskit": qiskit_gate.PhaseGate, "tq": tq.PhaseShift},
    # {'qiskit': qiskit_gate.?, 'tq': tq.Rot},
    # {'qiskit': qiskit_gate.?, 'tq': tq.MultiRZ},
    {"qiskit": qiskit_gate.CRXGate, "tq": tq.CRX},
    {"qiskit": qiskit_gate.CRYGate, "tq": tq.CRY},
    {"qiskit": qiskit_gate.CRZGate, "tq": tq.CRZ},
    # {'qiskit': qiskit_gate.?, 'tq': tq.CRot},
    {"qiskit": qiskit_gate.UGate, "tq": tq.U},
    {"qiskit": qiskit_gate.U1Gate, "tq": tq.U1},
    {"qiskit": qiskit_gate.U2Gate, "tq": tq.U2},
    {"qiskit": qiskit_gate.U3Gate, "tq": tq.U3},
    {"qiskit": qiskit_gate.CUGate, "tq": tq.CU},
    {"qiskit": qiskit_gate.CU1Gate, "tq": tq.CU1},
    # {'qiskit': qiskit_gate.?, 'tq': tq.CU2},
    {"qiskit": qiskit_gate.CU3Gate, "tq": tq.CU3},
    {"qiskit": qiskit_gate.ECRGate, "tq": tq.ECR},
    # {"qiskit": qiskit_library.QFT, "tq": tq.QFT},
    {"qiskit": qiskit_gate.SdgGate, "tq": tq.SDG},
    {"qiskit": qiskit_gate.TdgGate, "tq": tq.TDG},
    {"qiskit": qiskit_gate.SXdgGate, "tq": tq.SXDG},
    {"qiskit": qiskit_gate.CHGate, "tq": tq.CH},
    {"qiskit": qiskit_gate.CCZGate, "tq": tq.CCZ},
    {"qiskit": qiskit_gate.iSwapGate, "tq": tq.ISWAP},
    {"qiskit": qiskit_gate.CSGate, "tq": tq.CS},
    {"qiskit": qiskit_gate.CSdgGate, "tq": tq.CSDG},
    {"qiskit": qiskit_gate.CSXGate, "tq": tq.CSX},
    {"qiskit": qiskit_gate.DCXGate, "tq": tq.DCX},
    {"qiskit": qiskit_gate.XXMinusYYGate, "tq": tq.XXMINYY},
    {"qiskit": qiskit_gate.XXPlusYYGate, "tq": tq.XXPLUSYY},
    {"qiskit": qiskit_gate.C3XGate, "tq": tq.C3X},
    {"qiskit": qiskit_gate.RGate, "tq": tq.R},
    {"qiskit": qiskit_gate.C4XGate, "tq": tq.C4X},
    {"qiskit": qiskit_gate.RCCXGate, "tq": tq.RCCX},
    {"qiskit": qiskit_gate.RC3XGate, "tq": tq.RC3X},
    {"qiskit": qiskit_gate.GlobalPhaseGate, "tq": tq.GlobalPhase},
    {"qiskit": qiskit_gate.C3SXGate, "tq": tq.C3SX},
]

maximum_qubit_num = 5


def density_is_close(mat1: np.ndarray, mat2: np.ndarray):
    assert mat1.shape == mat2.shape
    return np.allclose(mat1, mat2)


class single_qubit_test(TestCase):
    '''
    Act one single qubit on all possible location of a quantum circuit,
    compare the density matrix between qiskit result and tq result.
    '''

    def compare_single_gate(self, gate_pair, qubit_num):
        passed = True
        for index in range(0, qubit_num):
            qdev = tq.NoiseDevice(n_wires=qubit_num, bsz=1, device="cpu", record_op=True)
            gate_pair['tq'](qdev, [index])
            mat1 = np.array(qdev.get_2d_matrix(0))
            rho_qiskit = qiskitDensity.from_label('0' * qubit_num)
            rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](), [qubit_num - 1 - index])
            mat2 = np.array(rho_qiskit.to_operator())
            if density_is_close(mat1, mat2):
                print("Test passed for %s gate on qubit %d when qubit_number is %d!" % (
                    gate_pair['name'], index, qubit_num))
            else:
                passed = False
                print("Test failed for %s gaet on qubit %d when qubit_number is %d!" % (
                    gate_pair['name'], index, qubit_num))
        return passed

    def test_single_gates(self):
        for qubit_num in range(1, maximum_qubit_num + 1):
            for i in range(0, len(single_gate_list)):
                self.assertTrue(self.compare_single_gate(single_gate_list[i], qubit_num))


class two_qubit_test(TestCase):
    '''
    Act two qubits gate on all possible location of a quantum circuit,
    compare the density matrix between qiskit result and tq result.
    '''

    def compare_two_qubit_gate(self, gate_pair, qubit_num):
        passed = True
        for index1 in range(0, qubit_num):
            for index2 in range(0, qubit_num):
                if index1 == index2:
                    continue
                qdev = tq.NoiseDevice(n_wires=qubit_num, bsz=1, device="cpu", record_op=True)
                gate_pair['tq'](qdev, [index1, index2])
                mat1 = np.array(qdev.get_2d_matrix(0))
                rho_qiskit = qiskitDensity.from_label('0' * qubit_num)
                rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](), [qubit_num - 1 - index1, qubit_num - 1 - index2])
                mat2 = np.array(rho_qiskit.to_operator())
                if density_is_close(mat1, mat2):
                    print("Test passed for %s gate on qubit (%d,%d) when qubit_number is %d!" % (
                        gate_pair['name'], index1, index2, qubit_num))
                else:
                    passed = False
                    print("Test failed for %s gate on qubit (%d,%d) when qubit_number is %d!" % (
                        gate_pair['name'], index1, index2, qubit_num))
        return passed

    def test_two_qubits_gates(self):
        for qubit_num in range(2, maximum_qubit_num + 1):
            for i in range(0, len(two_qubit_gate_list)):
                self.assertTrue(self.compare_two_qubit_gate(two_qubit_gate_list[i], qubit_num))


class three_qubit_test(TestCase):
    '''
    Act three qubits gates on all possible location of a quantum circuit,
    compare the density matrix between qiskit result and tq result.
    '''

    def compare_three_qubit_gate(self, gate_pair, qubit_num):
        passed = True
        for index1 in range(0, qubit_num):
            for index2 in range(0, qubit_num):
                if (index1 == index2):
                    continue
                for index3 in range(0, qubit_num):
                    if (index3 == index1) or (index3 == index2):
                        continue
                    qdev = tq.NoiseDevice(n_wires=qubit_num, bsz=1, device="cpu", record_op=True)
                    gate_pair['tq'](qdev, [index1, index2, index3])
                    mat1 = np.array(qdev.get_2d_matrix(0))
                    rho_qiskit = qiskitDensity.from_label('0' * qubit_num)
                    rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](),
                                                   [qubit_num - 1 - index1, qubit_num - 1 - index2,
                                                    qubit_num - 1 - index3])
                    mat2 = np.array(rho_qiskit.to_operator())
                    if density_is_close(mat1, mat2):
                        print("Test passed for %s gate on qubit (%d,%d,%d) when qubit_number is %d!" % (
                            gate_pair['name'], index1, index2, index3, qubit_num))
                    else:
                        passed = False
                        print("Test failed for %s gate on qubit (%d,%d,%d)  when qubit_number is %d!" % (
                            gate_pair['name'], index1, index2, index3, qubit_num))
        return passed

    def test_three_qubits_gates(self):
        for qubit_num in range(3, maximum_qubit_num + 1):
            for i in range(0, len(three_qubit_gate_list)):
                self.assertTrue(self.compare_three_qubit_gate(three_qubit_gate_list[i], qubit_num))


class random_layer_test(TestCase):
    '''
    Generate a single qubit random layer
    '''

    def single_qubit_random_layer(self, gatestrength):
        passed = True
        length = len(single_gate_list)
        for qubit_num in range(1, maximum_qubit_num + 1):
            qdev = tq.NoiseDevice(n_wires=qubit_num, bsz=1, device="cpu", record_op=True)
            rho_qiskit = qiskitDensity.from_label('0' * qubit_num)
            gate_num = int(gatestrength * qubit_num)
            for i in range(0, gate_num + 1):
                random_gate_index = randrange(length)
                gate_pair = single_gate_list[random_gate_index]
                random_qubit_index = randrange(qubit_num)
                gate_pair['tq'](qdev, [random_qubit_index])
                rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](), [qubit_num - 1 - random_qubit_index])

            mat1 = np.array(qdev.get_2d_matrix(0))
            mat2 = np.array(rho_qiskit.to_operator())

            if density_is_close(mat1, mat2):
                print(
                    "Test passed for single qubit gate random layer on qubit with %d gates when qubit_number is %d!" % (
                        gate_num, qubit_num))
            else:
                passed = False
                print(
                    "Test falied for single qubit gate random layer on qubit with %d gates when qubit_number is %d!" % (
                        gate_num, qubit_num))
        return passed

    def test_single_qubit_random_layer(self):
        repeat_num = 5
        gate_strength_list = [0.5, 1, 1.5, 2]
        for i in range(0, repeat_num):
            for gatestrength in gate_strength_list:
                self.assertTrue(self.single_qubit_random_layer(gatestrength))

    def two_qubit_random_layer(self, gatestrength):
        passed = True
        length = len(two_qubit_gate_list)
        for qubit_num in range(2, maximum_qubit_num + 1):
            qdev = tq.NoiseDevice(n_wires=qubit_num, bsz=1, device="cpu", record_op=True)
            rho_qiskit = qiskitDensity.from_label('0' * qubit_num)
            gate_num = int(gatestrength * qubit_num)
            for i in range(0, gate_num + 1):
                random_gate_index = randrange(length)
                gate_pair = two_qubit_gate_list[random_gate_index]
                random_qubit_index1 = randrange(qubit_num)
                random_qubit_index2 = randrange(qubit_num)
                while random_qubit_index2 == random_qubit_index1:
                    random_qubit_index2 = randrange(qubit_num)

                gate_pair['tq'](qdev, [random_qubit_index1, random_qubit_index2])
                rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](), [qubit_num - 1 - random_qubit_index1,
                                                                       qubit_num - 1 - random_qubit_index2])

            mat1 = np.array(qdev.get_2d_matrix(0))
            mat2 = np.array(rho_qiskit.to_operator())

            if density_is_close(mat1, mat2):
                print(
                    "Test passed for two qubit gate random layer on qubit with %d gates when qubit_number is %d!" % (
                        gate_num, qubit_num))
            else:
                passed = False
                print(
                    "Test falied for two qubit gate random layer on qubit with %d gates when qubit_number is %d!" % (
                        gate_num, qubit_num))
        return passed

    def test_two_qubit_random_layer(self):
        repeat_num = 5
        gate_strength_list = [0.5, 1, 1.5, 2]
        for i in range(0, repeat_num):
            for gatestrength in gate_strength_list:
                self.assertTrue(self.two_qubit_random_layer(gatestrength))

    def three_qubit_random_layer(self, gatestrength):
        passed = True
        length = len(three_qubit_gate_list)
        for qubit_num in range(3, maximum_qubit_num + 1):
            qdev = tq.NoiseDevice(n_wires=qubit_num, bsz=1, device="cpu", record_op=True)
            rho_qiskit = qiskitDensity.from_label('0' * qubit_num)
            gate_num = int(gatestrength * qubit_num)
            for i in range(0, gate_num + 1):
                random_gate_index = randrange(length)
                gate_pair = three_qubit_gate_list[random_gate_index]
                random_qubit_index1 = randrange(qubit_num)
                random_qubit_index2 = randrange(qubit_num)
                while random_qubit_index2 == random_qubit_index1:
                    random_qubit_index2 = randrange(qubit_num)
                random_qubit_index3 = randrange(qubit_num)
                while random_qubit_index3 == random_qubit_index1 or random_qubit_index3 == random_qubit_index2:
                    random_qubit_index3 = randrange(qubit_num)
                gate_pair['tq'](qdev, [random_qubit_index1, random_qubit_index2, random_qubit_index3])
                rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](), [qubit_num - 1 - random_qubit_index1,
                                                                       qubit_num - 1 - random_qubit_index2,
                                                                       qubit_num - 1 - random_qubit_index3])

            mat1 = np.array(qdev.get_2d_matrix(0))
            mat2 = np.array(rho_qiskit.to_operator())

            if density_is_close(mat1, mat2):
                print(
                    "Test passed for three qubit gate random layer on qubit with %d gates when qubit_number is %d!" % (
                        gate_num, qubit_num))
            else:
                passed = False
                print(
                    "Test falied for three qubit gate random layer on qubit with %d gates when qubit_number is %d!" % (
                        gate_num, qubit_num))
        return passed

    def test_three_qubit_random_layer(self):
        repeat_num = 5
        gate_strength_list = [0.5, 1, 1.5, 2]
        for i in range(0, repeat_num):
            for gatestrength in gate_strength_list:
                self.assertTrue(self.three_qubit_random_layer(gatestrength))

    def mix_random_layer(self, gatestrength):
        passed = True
        three_qubit_gate_length = len(three_qubit_gate_list)
        single_qubit_gate_length = len(single_gate_list)
        two_qubit_gate_length = len(two_qubit_gate_list)

        for qubit_num in range(3, maximum_qubit_num + 1):
            qdev = tq.NoiseDevice(n_wires=qubit_num, bsz=1, device="cpu", record_op=True)
            rho_qiskit = qiskitDensity.from_label('0' * qubit_num)
            gate_num = int(gatestrength * qubit_num)
            for i in range(0, gate_num + 1):
                random_gate_qubit_num = randrange(3)
                '''
                Add a single qubit gate
                '''
                if (random_gate_qubit_num == 0):
                    random_gate_index = randrange(single_qubit_gate_length)
                    gate_pair = single_gate_list[random_gate_index]
                    random_qubit_index = randrange(qubit_num)
                    gate_pair['tq'](qdev, [random_qubit_index])
                    rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](), [qubit_num - 1 - random_qubit_index])
                '''
                Add a two qubit gate
                '''
                if (random_gate_qubit_num == 1):
                    random_gate_index = randrange(two_qubit_gate_length)
                    gate_pair = two_qubit_gate_list[random_gate_index]
                    random_qubit_index1 = randrange(qubit_num)
                    random_qubit_index2 = randrange(qubit_num)
                    while random_qubit_index2 == random_qubit_index1:
                        random_qubit_index2 = randrange(qubit_num)
                    gate_pair['tq'](qdev, [random_qubit_index1, random_qubit_index2])
                    rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](), [qubit_num - 1 - random_qubit_index1,
                                                                           qubit_num - 1 - random_qubit_index2])
                '''
                Add a three qubit gate
                '''
                if (random_gate_qubit_num == 2):
                    random_gate_index = randrange(three_qubit_gate_length)
                    gate_pair = three_qubit_gate_list[random_gate_index]
                    random_qubit_index1 = randrange(qubit_num)
                    random_qubit_index2 = randrange(qubit_num)
                    while random_qubit_index2 == random_qubit_index1:
                        random_qubit_index2 = randrange(qubit_num)
                    random_qubit_index3 = randrange(qubit_num)
                    while random_qubit_index3 == random_qubit_index1 or random_qubit_index3 == random_qubit_index2:
                        random_qubit_index3 = randrange(qubit_num)
                    gate_pair['tq'](qdev, [random_qubit_index1, random_qubit_index2, random_qubit_index3])
                    rho_qiskit = rho_qiskit.evolve(gate_pair['qiskit'](), [qubit_num - 1 - random_qubit_index1,
                                                                           qubit_num - 1 - random_qubit_index2,
                                                                           qubit_num - 1 - random_qubit_index3])

            mat1 = np.array(qdev.get_2d_matrix(0))
            mat2 = np.array(rho_qiskit.to_operator())

            if density_is_close(mat1, mat2):
                print(
                    "Test passed for mix qubit gate random layer on qubit with %d gates when qubit_number is %d!" % (
                        gate_num, qubit_num))
            else:
                passed = False
                print(
                    "Test falied for mix qubit gate random layer on qubit with %d gates when qubit_number is %d!" % (
                        gate_num, qubit_num))
        return passed


    def test_mix_random_layer(self):
        repeat_num = 5
        gate_strength_list = [0.5, 1, 1.5, 2]
        for i in range(0, repeat_num):
            for gatestrength in gate_strength_list:
                self.assertTrue(self.mix_random_layer(gatestrength))