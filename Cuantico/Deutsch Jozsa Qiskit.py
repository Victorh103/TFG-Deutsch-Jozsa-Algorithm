from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit_aer import AerSimulator
import numpy as np
import matplotlib.pyplot as plt

def deutsch_jozsa_qiskit(n, oracle_type="constant"):
    #Creo un cirtuito con n+1 qubits
    circuit = QuantumCircuit(n+1, n)
    # 1º Inicializar el estado
    circuit.x(n)  # |1> en el último qubit
    
    # 2º Aplicar Hadamard a todos los qubits
    for i in range(n+1):
        circuit.h(i)
    
    # Barrera para separar las etapas del algoritmo
    circuit.barrier()
    
    # 3º Aplicar el oráculo
    if oracle_type == "constant":
        # Oráculo constante: U=0 o U=1
        if np.random.randint(2) == 1:
            circuit.z(n)  # Aplicar Z al último qubit
    else:  
        # Oráculo balanceado: aplicar CNOTs 
        for i in range(n):
            circuit.cx(i, n)
    
    # Barrera para separar el oráculo de la siguiente etapa
    circuit.barrier()
    
    # 4º Aplicar Hadamard a los n primeros qubits
    for i in range(n):
        circuit.h(i)
    
    # Barrera antes de la medición
    circuit.barrier()
    
    # 5º Medir los n primeros qubits
    for i in range(n):
        circuit.measure(i, i)
    

    # Ejecutar el circuito
    backend = AerSimulator()
    job = backend.run(circuit, shots=1024)
    
    result = job.result()
    counts = result.get_counts() 
    
    # Interpretar el resultado
    if '0'*n in counts and len(counts) == 1:
        return "La función es constante", circuit, counts
    else:
        return "La función es balanceada", circuit, counts

n = 4  # Número de qubits 
oracle_type = "constant"  # Cambiar a "constant" o "balanced"

result, circuit, counts = deutsch_jozsa_qiskit(n, oracle_type)

# Visualizar el circuito
print("\nCircuito implementado:")
print(circuit.draw())

print(f"La función es: {result}")
