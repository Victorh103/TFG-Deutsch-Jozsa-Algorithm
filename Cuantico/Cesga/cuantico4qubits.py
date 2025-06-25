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

def deutsch_jozsa_circuit(n=4, oracle_type="constant", oracle_case=0):
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

def ejecutar_experimento_deutsch_jozsa_estadistico():
    n = 4
    shots = 1
    
    total_pruebas = 300
    num_balanced = 250
    num_constant = 50
    
    qubit_layout = [12, 13, 19, 20, 6]

    resultados = {
        "configuracion": {
            "total_pruebas": total_pruebas,
            "num_balanced": num_balanced,
            "num_constant": num_constant,
            "relacion": "3:1",
            "n_qubits": n,
            "shots_por_circuito": shots,
            "qubit_layout": qubit_layout
        },
        "pruebas": [],
        "estadisticas": {}
    }
    
    aciertos_constant = 0
    aciertos_balanced = 0
    fallos_constant = 0
    fallos_balanced = 0
    
    pruebas_lista = []
    
    for i in range(num_constant):
        oracle_case = i % 2
        pruebas_lista.append({
            "oracle_type": "constant",
            "oracle_case": oracle_case,
            "expected": "constant"
        })
    
    for i in range(num_balanced):
        oracle_case = random.randint(1, 2**n - 2)
        pruebas_lista.append({
            "oracle_type": "balanced",
            "oracle_case": oracle_case,
            "expected": "balanced"
        })
    
    random.shuffle(pruebas_lista)
        
    for i, prueba_config in enumerate(pruebas_lista):
        print(f"\rEjecutando prueba {i+1}/{total_pruebas} ({prueba_config['oracle_type']})", end="")
        
        oracle_type = prueba_config["oracle_type"]
        oracle_case = prueba_config["oracle_case"]
        expected = prueba_config["expected"]
        
        circuit = deutsch_jozsa_circuit(n, oracle_type, oracle_case)
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
        total_shots = sum(counts.values())
        
        if zeros_count / total_shots > 0.5:
            classification = "constant"
        else:
            classification = "balanced"
            
        correct = (classification == expected)
        
        if oracle_type == "constant":
            if correct:
                aciertos_constant += 1
            else:
                fallos_constant += 1
        else:
            if correct:
                aciertos_balanced += 1
            else:
                fallos_balanced += 1
        
        resultado = {
            "prueba_num": i + 1,
            "tipo": oracle_type,
            "oracle_type": oracle_type,
            "oracle_case": oracle_case,
            "expected": expected,
            "classified": classification,
            "counts": counts,
            "correct": correct,
            "zeros_percentage": zeros_count / total_shots
        }
        
        resultados["pruebas"].append(resultado)
    
    print()
    
    precision_constant = aciertos_constant / num_constant if num_constant > 0 else 0
    precision_balanced = aciertos_balanced / num_balanced if num_balanced > 0 else 0
    precision_total = (aciertos_constant + aciertos_balanced) / total_pruebas
    
    recall_constant = aciertos_constant / (aciertos_constant + fallos_constant) if (aciertos_constant + fallos_constant) > 0 else 0
    recall_balanced = aciertos_balanced / (aciertos_balanced + fallos_balanced) if (aciertos_balanced + fallos_balanced) > 0 else 0
    
    constant_as_balanced = fallos_constant
    balanced_as_constant = fallos_balanced
    
    estadisticas = {
        "precision": {
            "constant": precision_constant,
            "balanced": precision_balanced,
            "total": precision_total
        },
        "recall": {
            "constant": recall_constant,
            "balanced": recall_balanced
        },
        "aciertos": {
            "constant": aciertos_constant,
            "balanced": aciertos_balanced,
            "total": aciertos_constant + aciertos_balanced
        },
        "fallos": {
            "constant": fallos_constant,
            "balanced": fallos_balanced,
            "total": fallos_constant + fallos_balanced
        },
        "totales": {
            "constant": num_constant,
            "balanced": num_balanced,
            "total": total_pruebas
        },
        "matriz_confusion": {
            "constant_correct": aciertos_constant,
            "constant_as_balanced": constant_as_balanced,
            "balanced_correct": aciertos_balanced,
            "balanced_as_constant": balanced_as_constant
        },
        "porcentajes": {
            "precision_constant_pct": precision_constant * 100,
            "precision_balanced_pct": precision_balanced * 100,
            "precision_total_pct": precision_total * 100
        }
    }
    
    resultados["estadisticas"] = estadisticas
    
    print("\n" + "="*60)
    print("RESULTADOS DEL EXPERIMENTO DEUTSCH-JOZSA")
    print("="*60)
 
    
    print("PRECISIÓN (Accuracy):")
    print(f"  Total: {aciertos_constant + aciertos_balanced}/{total_pruebas} ({precision_total:.2%})")
    print(f"  Funciones constantes: {aciertos_constant}/{num_constant} ({precision_constant:.2%})")
    print(f"  Funciones balanceadas: {aciertos_balanced}/{num_balanced} ({precision_balanced:.2%})")
    print()
    
    output_file = "4qubits.json"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(resultados, f, indent=2)
    
if __name__ == "__main__":
    random.seed(42)
    resultados = ejecutar_experimento_deutsch_jozsa_estadistico()