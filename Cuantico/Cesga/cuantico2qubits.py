import os
import numpy as np
import json
import random
import logging

os.environ["ZMQ_SERVER"] = "tcp://127.0.0.1:5556"

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import HGate, XGate
from qmiotools.integrations.qiskitqmio.qmiobackend import QmioBackend

backend = QmioBackend(
    logging_filename=None, 
    logging_level=logging.ERROR
)

def generar_todos_los_casos_balanceados(n):
    casos_balanceados = []
    total_entradas = 2**n
    
    for i in range(1, 2**total_entradas - 1):
        num_unos = bin(i).count('1')
        if num_unos == total_entradas // 2:
            casos_balanceados.append(i)
    
    return casos_balanceados

def deutsch_jozsa_circuit(n=2, oracle_type="constant", oracle_case=0):
    circuit = QuantumCircuit(n+1, n)
    
    circuit.x(n)
    
    for i in range(n+1):
        circuit.h(i)
    
    if oracle_type == "constant":
        if oracle_case == 1:
            circuit.z(n)
    else:
        for i in range(n):
            if (oracle_case >> i) & 1:
                circuit.cx(i, n)
    
    for i in range(n):
        circuit.h(i)
    
    for i in range(n):
        circuit.measure(i, i)
    
    return circuit

def ejecutar_experimento():
    n = 2
    shots = 1
    qubit_layout = [19, 20, 13]
    
    num_constant = 100
    num_balanced = 100
    total_pruebas = 200
    
    casos_constantes = [0, 1]
    casos_balanceados = generar_todos_los_casos_balanceados(n)
    
    resultados = {
        "pruebas": [],
        "estadisticas": {}
    }
    
    aciertos_constant = 0
    aciertos_balanced = 0
    
    for i in range(num_constant):
        print(f"\rEjecutando prueba constante {i+1}/{num_constant}", end="")
        
        oracle_case = random.choice(casos_constantes)
        circuit = deutsch_jozsa_circuit(n, "constant", oracle_case)
        
        transpiled_circuit = transpile(
            circuit,
            backend,
            initial_layout=qubit_layout,
            optimization_level=2
        )
        
        job = backend.run(transpiled_circuit, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        zeros_count = counts.get('0'*n, 0)
        classification = "constant" if zeros_count > 0 else "balanced"
        correct = (classification == "constant")
        
        if correct:
            aciertos_constant += 1
        
        resultados["pruebas"].append({
            "prueba_num": i + 1,
            "tipo": "constant",
            "oracle_case": oracle_case,
            "counts": counts,
            "classification": classification,
            "correct": correct
        })
    
    print()
    
    for i in range(num_balanced):
        print(f"\rEjecutando prueba balanceada {i+1}/{num_balanced}", end="")
        
        oracle_case = random.choice(casos_balanceados)
        circuit = deutsch_jozsa_circuit(n, "balanced", oracle_case)
        
        transpiled_circuit = transpile(
            circuit,
            backend,
            initial_layout=qubit_layout,
            optimization_level=2
        )
        
        job = backend.run(transpiled_circuit, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        zeros_count = counts.get('0'*n, 0)
        classification = "constant" if zeros_count > 0 else "balanced"
        correct = (classification == "balanced")
        
        if correct:
            aciertos_balanced += 1
        
        resultados["pruebas"].append({
            "prueba_num": num_constant + i + 1,
            "tipo": "balanced",
            "oracle_case": oracle_case,
            "counts": counts,
            "classification": classification,
            "correct": correct
        })
    
    print("\n")
    
    precision_constant = aciertos_constant / num_constant
    precision_balanced = aciertos_balanced / num_balanced
    precision_total = (aciertos_constant + aciertos_balanced) / total_pruebas
    
    estadisticas = {
        "precision_constant": precision_constant,
        "precision_balanced": precision_balanced,
        "precision_total": precision_total,
        "aciertos_constant": aciertos_constant,
        "aciertos_balanced": aciertos_balanced,
        "total_constant": num_constant,
        "total_balanced": num_balanced
    }
    
    resultados["estadisticas"] = estadisticas
    
    print(f"Precisión total: {aciertos_constant + aciertos_balanced}/{total_pruebas} ({precision_total:.2%})")
    print(f"Precisión en funciones constantes: {aciertos_constant}/{num_constant} ({precision_constant:.2%})")
    print(f"Precisión en funciones balanceadas: {aciertos_balanced}/{num_balanced} ({precision_balanced:.2%})")
    
    output_file = "2qubits.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(resultados, f, indent=2)
    
    return resultados

if __name__ == "__main__":
    ejecutar_experimento()