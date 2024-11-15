from qiskit import QuantumCircuit, transpile
import qiskit_aer as qe
import numpy as np
from rest_framework import status
from rest_framework.response import Response

from .models import KeyMaterial


def generate_bb84_keys(num_keys, num_bits_per_key):
    """Generate multiple keys using the BB84 protocol"""
    all_keys = []

    # Check if the size of the keys is a multiple of 8
    if num_bits_per_key % 8 != 0:
        return Response({"error": "Key size must be a multiple of 8"}, status=status.HTTP_400_BAD_REQUEST)

    for _ in range(num_keys):
        # Random generation of bits and bases for each key.
        alice_bits = np.random.randint(2, size=num_bits_per_key)
        alice_basis = np.random.randint(2, size=num_bits_per_key)
        bob_basis = np.random.randint(2, size=num_bits_per_key)

        # Preparation of qubits.
        qc = QuantumCircuit(num_bits_per_key, num_bits_per_key)
        for i in range(num_bits_per_key):
            if alice_bits[i] == 1:  # Bit de base
                qc.x(i)
            if alice_basis[i] == 1:  # Base diagonale
                qc.h(i)

        qc.barrier()

        # Measurement by Bob.
        for i in range(num_bits_per_key):
            if bob_basis[i] == 1:
                qc.h(i)  # If Bob's basis is diagonal, apply H before measuring.

        qc.barrier()

        # Measurement of Bob's bits
        for i in range(num_bits_per_key):
            qc.measure(i, i)

        # Execution with simulation (backend qasm_simulator).
        simulation = qe.Aer.get_backend('qasm_simulator')
        job = simulation.run(transpile(qc, simulation), shots=1, memory=True)
        result = job.result()
        measurements = result.get_memory()[0]

        # Retrieve Bob's bits
        bob_bits = [int(measurement) for measurement in measurements]
        bob_bits.reverse()

        # Generate the key from the matching bases between Alice and Bob.
        key = [int(alice_bits[i]) for i in range(num_bits_per_key) if alice_basis[i] == bob_basis[i]]

        # Add the key to the list of generated keys.
        all_keys.append(key)

    return all_keys
