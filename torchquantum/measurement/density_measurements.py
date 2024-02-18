import random

import torch
import torchquantum as tq
import torchquantum.functional as tqf
import numpy as np
from torchquantum.macro import F_DTYPE

from typing import Union, List
from collections import Counter, OrderedDict

from torchquantum.functional import mat_dict
# from .operator import op_name_dict, Observable
import torchquantum.operator as op
from copy import deepcopy
import matplotlib.pyplot as plt
from .measurements import gen_bitstrings
from .measurements import find_observable_groups

__all__ = [
    "expval_joint_sampling_grouping",
    "expval_joint_analytical",
    "expval_joint_sampling",
    "expval",
    "measure",
    "MeasureAll_Density"
]


def measure(noisedev: tq.NoiseDevice, n_shots=1024, draw_id=None):
    """Measure the target density matrix and obtain classical bitstream distribution
    Args:
        noisedev: input tq.NoiseDevice
        n_shots: number of simulated shots
    Returns:
        distribution of bitstrings
    """
    bitstring_candidates = gen_bitstrings(noisedev.n_wires)

    state_mag = noisedev.get_probs_1d().abs().detach().cpu().numpy()
    distri_all = []

    for state_mag_one in state_mag:
        state_prob_one = state_mag_one
        measured = random.choices(
            population=bitstring_candidates,
            weights=state_prob_one,
            k=n_shots,
        )
        counter = Counter(measured)
        counter.update({key: 0 for key in bitstring_candidates})
        distri = dict(counter)
        distri = OrderedDict(sorted(distri.items()))
        distri_all.append(distri)

    if draw_id is not None:
        plt.bar(distri_all[draw_id].keys(), distri_all[draw_id].values())
        plt.xticks(rotation="vertical")
        plt.xlabel("bitstring [qubit0, qubit1, ..., qubitN]")
        plt.title("distribution of measured bitstrings")
        plt.show()
    return distri_all


def expval_joint_sampling_grouping(
        noisedev: tq.NoiseDevice,
        observables: List[str],
        n_shots_per_group=1024,
):
    assert len(observables) == len(set(observables)), "each observable should be unique"
    # key is the group, values is the list of sub-observables
    obs = []
    for observable in observables:
        obs.append(observable.upper())
    # firstly find the groups
    groups = find_observable_groups(obs)

    # rotation to the desired basis
    n_wires = noisedev.n_wires
    paulix = op.op_name_dict["paulix"]
    pauliy = op.op_name_dict["pauliy"]
    pauliz = op.op_name_dict["pauliz"]
    iden = op.op_name_dict["i"]
    pauli_dict = {"X": paulix, "Y": pauliy, "Z": pauliz, "I": iden}

    expval_all_obs = {}
    for obs_group, obs_elements in groups.items():
        # for each group need to clone a new qdev and its states
        noisedev_clone = tq.NoiseDevice(n_wires=noisedev.n_wires, bsz=noisedev.bsz, device=noisedev.device)
        noisedev_clone.clone_densities(noisedev.densities)

        for wire in range(n_wires):
            for rotation in pauli_dict[obs_group[wire]]().diagonalizing_gates():
                rotation(noisedev_clone, wires=wire)

        # measure
        distributions = measure(noisedev_clone, n_shots=n_shots_per_group)
        # interpret the distribution for different observable elements
        for obs_element in obs_elements:
            expval_all = []
            mask = np.ones(len(obs_element), dtype=bool)
            mask[np.array([*obs_element]) == "I"] = False

            for distri in distributions:
                n_eigen_one = 0
                n_eigen_minus_one = 0
                for bitstring, n_count in distri.items():
                    if np.dot(list(map(lambda x: eval(x), [*bitstring])), mask).sum() % 2 == 0:
                        n_eigen_one += n_count
                    else:
                        n_eigen_minus_one += n_count

                expval = n_eigen_one / n_shots_per_group + (-1) * n_eigen_minus_one / n_shots_per_group

                expval_all.append(expval)
            expval_all_obs[obs_element] = torch.tensor(expval_all, dtype=F_DTYPE)

    return expval_all_obs


def expval_joint_sampling(
        qdev: tq.NoiseDevice,
        observable: str,
        n_shots=1024,
):
    return


def expval_joint_analytical(
        noisedev: tq.NoiseDevice,
        observable: str,
        n_shots=1024
):
    """
     Compute the expectation value of a joint observable from sampling
     the measurement bistring
     Args:
         qdev: the quantum device
         observable: the joint observable, on the qubit 0, 1, 2, 3, etc in this order
     Returns:
         the expectation value
     Examples:
     >>> import torchquantum as tq
     >>> import torchquantum.functional as tqf
     >>> x = tq.NoiseDevice(n_wires=2)
     >>> tqf.hadamard(x, wires=0)
     >>> tqf.x(x, wires=1)
     >>> tqf.cnot(x, wires=[0, 1])
     >>> print(expval_joint_sampling(x, 'II', n_shots=8192))
     tensor([[0.9997]])
     >>> print(expval_joint_sampling(x, 'XX', n_shots=8192))
     tensor([[0.9991]])
     >>> print(expval_joint_sampling(x, 'ZZ', n_shots=8192))
     tensor([[-0.9980]])
     """
    # rotation to the desired basis
    n_wires = noisedev.n_wires
    paulix = op.op_name_dict["paulix"]
    pauliy = op.op_name_dict["pauliy"]
    pauliz = op.op_name_dict["pauliz"]
    iden = op.op_name_dict["i"]
    pauli_dict = {"X": paulix, "Y": pauliy, "Z": pauliz, "I": iden}

    noisedev_clone = tq.NoiseDevice(n_wires=noisedev.n_wires, bsz=noisedev.bsz, device=noisedev.device)
    noisedev_clone.clone_densities(noisedev.densities)

    observable = observable.upper()
    for wire in range(n_wires):
        for rotation in pauli_dict[observable[wire]]().diagonalizing_gates():
            rotation(noisedev_clone, wires=wire)

    mask = np.ones(len(observable), dtype=bool)
    mask[np.array([*observable]) == "I"] = False

    expval_all = []
    # measure
    distributions = measure(noisedev_clone, n_shots=n_shots)
    for distri in distributions:
        n_eigen_one = 0
        n_eigen_minus_one = 0
        for bitstring, n_count in distri.items():
            if np.dot(list(map(lambda x: eval(x), [*bitstring])), mask).sum() % 2 == 0:
                n_eigen_one += n_count
            else:
                n_eigen_minus_one += n_count

        expval = n_eigen_one / n_shots + (-1) * n_eigen_minus_one / n_shots
        expval_all.append(expval)

    return torch.tensor(expval_all, dtype=F_DTYPE)


def expval(
        noisedev: tq.NoiseDevice,
        wires: Union[int, List[int]],
        observables: Union[op.Observable, List[op.Observable]],
):
    all_dims = np.arange(noisedev.n_wires+1)
    if isinstance(wires, int):
        wires = [wires]
        observables = [observables]

    # rotation to the desired basis
    for wire, observable in zip(wires, observables):
        for rotation in observable.diagonalizing_gates():
            rotation(noisedev, wires=wire)

    # compute magnitude
    state_mag = noisedev.get_probs_1d()
    bsz = state_mag.shape[0]
    state_mag = torch.reshape(state_mag, [bsz] + [2] * noisedev.n_wires)
    expectations = []
    for wire, observable in zip(wires, observables):
        # compute marginal magnitude
        reduction_dims = np.delete(all_dims, [0, wire + 1])
        if reduction_dims.size == 0:
            probs = state_mag
        else:
            probs = state_mag.sum(list(reduction_dims))
        res = probs.mv(observable.eigvals.real.to(probs.device))
        expectations.append(res)

    return torch.stack(expectations, dim=-1)


class MeasureAll_Density(tq.QuantumModule):
    """Obtain the expectation value of all the qubits."""

    def __init__(self, obs, v_c_reg_mapping=None):
        super().__init__()
        self.obs = obs
        self.v_c_reg_mapping = v_c_reg_mapping

    def forward(self, qdev: tq.NoiseDevice):
        x = expval(qdev, list(range(qdev.n_wires)), [self.obs()] * qdev.n_wires)

        if self.v_c_reg_mapping is not None:
            c2v_mapping = self.v_c_reg_mapping["c2v"]
            """
            the measurement is not normal order, need permutation
            """
            perm = []
            for k in range(x.shape[-1]):
                if k in c2v_mapping.keys():
                    perm.append(c2v_mapping[k])
            x = x[:, perm]

        if self.noise_model_tq is not None and self.noise_model_tq.is_add_noise:
            return self.noise_model_tq.apply_readout_error(x)
        else:
            return x

    def set_v_c_reg_mapping(self, mapping):
        self.v_c_reg_mapping = mapping


if __name__ == '__main__':
    print("Yes")
    qdev = tq.NoiseDevice(n_wires=2, bsz=5, device="cpu", record_op=True)  # use device='cuda' for GPU
    qdev.h(wires=0)
    qdev.cnot(wires=[0, 1])
    tqf.h(qdev, wires=1)
    tqf.x(qdev, wires=1)
    op = tq.RX(has_params=True, trainable=True, init_params=0.5)
    op(qdev, wires=0)

    # measure the state on z basis
    print(tq.measure(qdev, n_shots=1024))

    # obtain the expval on a observable
    expval = expval_joint_sampling(qdev, 'II', 100000)
    # expval_ana = expval_joint_analytical(qdev, 'II')
    print(expval)