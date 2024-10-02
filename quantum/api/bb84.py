from qiskit import QuantumCircuit, transpile
import qiskit_aer as qe
import numpy as np
from rest_framework import status
from rest_framework.response import Response

from .models import KeyMaterial


def generate_bb84_keys(num_keys, num_bits_per_key):
    """Générer plusieurs clés via le protocole BB84"""
    all_keys = []

    # Vérifier si la taille des clés est bien un multiple de 8
    if num_bits_per_key % 8 != 0:
        return Response({"error": "Key size must be a multiple of 8"}, status=status.HTTP_400_BAD_REQUEST)

    for _ in range(num_keys):
        # Génération aléatoire des bits et bases pour chaque clé
        alice_bits = np.random.randint(2, size=num_bits_per_key)
        alice_basis = np.random.randint(2, size=num_bits_per_key)
        bob_basis = np.random.randint(2, size=num_bits_per_key)

        # Préparation des qubits
        qc = QuantumCircuit(num_bits_per_key, num_bits_per_key)
        for i in range(num_bits_per_key):
            if alice_bits[i] == 1:  # Bit de base
                qc.x(i)
            if alice_basis[i] == 1:  # Base diagonale
                qc.h(i)

        qc.barrier()

        # Mesure par Bob
        for i in range(num_bits_per_key):
            if bob_basis[i] == 1:
                qc.h(i)  # Si la base de Bob est diagonale, applique H avant de mesurer

        qc.barrier()

        # Mesure des bits de Bob
        for i in range(num_bits_per_key):
            qc.measure(i, i)

        # Exécution avec simulation (backend qasm_simulator)
        simulation = qe.Aer.get_backend('qasm_simulator')
        job = simulation.run(transpile(qc, simulation), shots=1, memory=True)
        result = job.result()
        measurements = result.get_memory()[0]

        # Récupérer les bits de Bob
        bob_bits = [int(measurement) for measurement in measurements]
        bob_bits.reverse()

        # Générer la clé à partir des bases correspondantes entre Alice et Bob
        key = [alice_bits[i] for i in range(num_bits_per_key) if alice_basis[i] == bob_basis[i]]

        # Ajouter la clé à la liste des clés générées
        all_keys.append(key)

    return all_keys
