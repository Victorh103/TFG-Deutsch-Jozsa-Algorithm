from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, phase_damping_error, amplitude_damping_error
import numpy as np
import matplotlib.pyplot as plt
import random
from tqdm import tqdm
import csv

def deutsch_jozsa_qiskit(n, oracle_type="constant", oracle_case=0, noise_level=0, noise_type="depolarizing"):
    """
    Implementación del algoritmo Deutsch-Jozsa con Qiskit
    
    Args:
        n: Número de qubits (excluyendo el auxiliar)
        oracle_type: "constant" o "balanced"
        oracle_case: Configuración específica del oráculo
        noise_level: Nivel de ruido 
        noise_type: Tipo de ruido ("depolarizing", "dephasing", "damping")
        
    Returns:
        resultado clasificado y circuito
    """
    # Crear un circuito con n+1 qubits
    circuit = QuantumCircuit(n+1, n)
    
    # 1º Inicializar el estado
    circuit.x(n)  # |1> en el último qubit
    
    # 2º Aplicar Hadamard a todos los qubits
    for i in range(n+1):
        circuit.h(i)
    
    circuit.barrier()
    
    # 3º Aplicar el oráculo
    if oracle_type == "constant":
        # Oráculo constante: U=0 o U=1
        if oracle_case == 1:
            circuit.z(n)  # Aplicar Z al último qubit si oracle_case=1
    else:  
        # Oráculo balanceado: aplicar CNOT según oracle_case
        for i in range(n):
            if (oracle_case >> i) & 1:
                circuit.cx(i, n)
    
    circuit.barrier()
    
    # 4º Hadamard a los n primeros qubits
    for i in range(n):
        circuit.h(i)
    
    circuit.barrier()
    
    # 5º Medir los n primeros qubits
    for i in range(n):
        circuit.measure(i, i)
    
    # Modelo de ruido
    noise_model = None
    if noise_level > 0:
        noise_model = NoiseModel()
        
        # Seleccionar tipo de error
        if noise_type == "depolarizing":
            # Error de despolarización
            error1 = depolarizing_error(noise_level, 1)  # Para operaciones de 1 qubit
            error2 = depolarizing_error(noise_level, 2)  # Para operaciones de 2 qubits
        elif noise_type == "dephasing":
            # Error de desfase 
            error1 = phase_damping_error(noise_level)    # Para 1 qubit
            # Para 2 qubits, aplicar el error de forma independiente
            error2 = error1.tensor(error1)  # Tensor product para 2 qubits independientes
        elif noise_type == "damping":
            # Error de decaimiento de amplitud
            error1 = amplitude_damping_error(noise_level)  # Para 1 qubit
            # Para 2 qubits, aplicar el error de forma independiente
            error2 = error1.tensor(error1)  # Tensor product para 2 qubits independientes
        else:
            # Por defecto, usar despolarización
            error1 = depolarizing_error(noise_level, 1)
            error2 = depolarizing_error(noise_level, 2)
            
        # Aplicar errores a las puertas
        noise_model.add_all_qubit_quantum_error(error1, ['h', 'x', 'z'])
        noise_model.add_all_qubit_quantum_error(error2, ['cx'])
    
    # Ejecutar el simulador
    backend = AerSimulator()
    if noise_model is not None:
        job = backend.run(circuit, shots=1, noise_model=noise_model)  
    else:
        job = backend.run(circuit, shots=1)
    result = job.result()
    counts = result.get_counts()
    
    # Interpretar el resultado
    if '0'*n in counts and len(counts) == 1:
        return "constant", circuit
    else:
        return "balanced", circuit

def generate_balanced_oracle_case(n):
    """
    Genera un caso de oráculo balanceado aleatorio para n qubits.
    
    Args:
        n: Número de qubits
    
    Returns:
        Entero que representa el caso del oráculo balanceado
    """
    # Para n qubits, tenemos 2^n posibles entradas
    # Un oráculo balanceado tiene exactamente 2^(n-1) entradas que mapean a 1
    
    # Generamos un número aleatorio entre 1 y 2^n - 1 que represente qué qubits aplicar CNOT
    return random.randint(1, (2**n) - 1)

def evaluate_accuracy_with_error(n, noise_levels, num_tests=100, num_runs=10, noise_type="depolarizing"):
    """
    Evalúa la precisión del algoritmo DJ con múltiples ejecuciones para calcular error estadístico
    
    Args:
        n: Número de qubits (excluyendo el auxiliar)
        noise_levels: Lista de niveles de ruido a probar
        num_tests: Número de pruebas aleatorias para cada nivel de ruido en cada run
        num_runs: Número de ejecuciones independientes para calcular estadísticas
        noise_type: Tipo de ruido a usar ("depolarizing", "dephasing", "damping")
    
    Returns:
        Tupla con (medias, desviaciones_estándar) para cada nivel de ruido
    """
    accuracy_means = []
    accuracy_stds = []
    
    for noise in tqdm(noise_levels, desc=f"Evaluando niveles de ruido ({noise_type})"):
        # Almacenar resultados de múltiples ejecuciones
        run_accuracies = []
        
        for run in range(num_runs):
            correct_tests = 0
            
            # Probar funciones constantes y balanceadas
            for _ in range(num_tests // 2):
                # Función constante
                oracle_case = random.choice([0, 1])  # 0 o 1 para constante
                result, _ = deutsch_jozsa_qiskit(n, "constant", oracle_case, noise, noise_type)
                if result == "constant":
                    correct_tests += 1
                    
                # Función balanceada
                oracle_case = generate_balanced_oracle_case(n)
                result, _ = deutsch_jozsa_qiskit(n, "balanced", oracle_case, noise, noise_type)
                if result == "balanced":
                    correct_tests += 1
            
            # Calcular precisión para esta ejecución
            accuracy = correct_tests / num_tests
            run_accuracies.append(accuracy)
        
        # Calcular estadísticas
        mean_accuracy = np.mean(run_accuracies)
        std_accuracy = np.std(run_accuracies, ddof=1)  # Usar ddof=1 para muestra
        
        accuracy_means.append(mean_accuracy)
        accuracy_stds.append(std_accuracy)
        
        print(f"Nivel de ruido {noise:.3f}: {mean_accuracy:.3f} ± {std_accuracy:.3f} ({mean_accuracy:.2%} ± {std_accuracy:.2%})")
    
    return accuracy_means, accuracy_stds

def plot_accuracy_vs_noise_with_errors(noise_levels, accuracy_results_dict, error_results_dict, n, num_tests, num_runs):
    """
    Genera una gráfica de la precisión vs nivel de ruido con barras de error para diferentes tipos de ruido
    
    Args:
        noise_levels: Lista de niveles de ruido evaluados
        accuracy_results_dict: Diccionario con las medias para cada tipo de ruido
        error_results_dict: Diccionario con las desviaciones estándar para cada tipo de ruido
        n: Número de qubits
        num_tests: Número de pruebas realizadas por ejecución
        num_runs: Número de ejecuciones independientes
    """
    plt.figure(figsize=(12, 8))
    
    colors = {
        'depolarizing': '#1f77b4',  # Azul
        'dephasing': '#ff7f0e',     # Naranja
        'damping': '#2ca02c'        # Verde
    }
    
    names = {
        'depolarizing': 'Error de Despolarización',
        'dephasing': 'Error de Desfase',
        'damping': 'Error de Decaimiento'
    }
    
    # Crear gráficas para cada tipo de ruido con barras de error
    for noise_type in accuracy_results_dict.keys():
        accuracy_means = accuracy_results_dict[noise_type]
        accuracy_errors = error_results_dict[noise_type]
        
        plt.errorbar(noise_levels, accuracy_means, yerr=accuracy_errors,
                    marker='o', linestyle='-', capsize=5, capthick=2,
                    color=colors[noise_type], linewidth=2, markersize=8,
                    markerfacecolor=colors[noise_type], markeredgecolor='black',
                    markeredgewidth=1.5, elinewidth=2,
                    label=names[noise_type])
    
    # Añadir una línea de precisión aleatoria en y=0.5 
    plt.axhline(y=0.5, color='r', linestyle='--', alpha=0.7, linewidth=2, label='Precisión aleatoria')
    
    plt.xlabel('Nivel de Ruido', fontsize=14, fontweight='bold')
    plt.ylabel('Tasa de Aciertos', fontsize=14, fontweight='bold')
    plt.title(f'Algoritmo Deutsch-Jozsa: Análisis frente a Diferentes Tipos de Ruido\n({n} qubits, {num_tests} pruebas/ejecución, {num_runs} ejecuciones)', 
              fontsize=16, pad=20)
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # Personalizar ejes
    plt.xlim([min(noise_levels)-0.02, max(noise_levels)+0.02])
    plt.ylim([0, 1.05])
    
    # Formatear ticks
    plt.xticks(fontsize=12)
    plt.yticks([0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0], 
               ['0%', '20%', '40%', '50%', '60%', '80%', '100%'], 
               fontsize=12)
    
    # Añadir leyenda
    plt.legend(fontsize=12, loc='lower left', frameon=True, shadow=True)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar la figura con alta resolución
    plt.savefig('deutsch_jozsa_noise_analysis_with_errors.png', dpi=300, bbox_inches='tight')
    
    return plt.gcf()

def save_results_to_csv_with_errors(noise_levels, accuracy_results_dict, error_results_dict, filename="dj_noise_results_with_errors.csv"):
    """
    Guarda los resultados con errores en un archivo CSV
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Escribir encabezados
        headers = ['Nivel de Ruido']
        for noise_type in accuracy_results_dict.keys():
            headers.extend([f'{noise_type}_media', f'{noise_type}_error'])
        writer.writerow(headers)
        
        # Escribir datos
        for i, noise in enumerate(noise_levels):
            row = [noise]
            for noise_type in accuracy_results_dict.keys():
                row.extend([accuracy_results_dict[noise_type][i], error_results_dict[noise_type][i]])
            writer.writerow(row)
    
    print(f"\nResultados con errores guardados en {filename}")

if __name__ == "__main__":
    # Parámetros de la simulación
    n = 4  # Número de qubits
    noise_levels = np.linspace(0, 1, 30)  # 30 niveles de ruido entre 0 y 0.5
    num_tests = 100  # Número de pruebas para cada nivel por ejecución
    num_runs = 20   # Número de ejecuciones independientes para estadísticas
    noise_types = ["depolarizing", "dephasing", "damping"]

    # Ejecutar la evaluación
    print(f"Evaluando algoritmo Deutsch-Jozsa con {n} qubits")
    print(f"Realizando {num_tests} pruebas × {num_runs} ejecuciones para cada uno de los {len(noise_levels)} niveles de ruido")
    print(f"Comparando {len(noise_types)} tipos de ruido: {', '.join(noise_types)}")

    # Almacenar los resultados de los distintos tipos de ruido
    accuracy_results_dict = {}
    error_results_dict = {}

    # Evaluar la precisión para cada tipo de ruido
    for noise_type in noise_types:
        print(f"\nEvaluando modelo de ruido: {noise_type}")
        accuracy_means, accuracy_stds = evaluate_accuracy_with_error(n, noise_levels, num_tests, num_runs, noise_type)
        accuracy_results_dict[noise_type] = accuracy_means
        error_results_dict[noise_type] = accuracy_stds

    # Graficar resultados con barras de error
    fig = plot_accuracy_vs_noise_with_errors(noise_levels, accuracy_results_dict, error_results_dict, n, num_tests, num_runs)

    # Mostrar resultados finales para cada tipo de ruido
    for noise_type in noise_types:
        print(f"\nResumen de resultados para {noise_type}:")
        print("=" * 50)
        print(f"{'Nivel de Ruido':<15} | {'Media ± Error':<20} | {'Rango':<15}")
        print("-" * 52)
        for noise, mean, std in zip(noise_levels, accuracy_results_dict[noise_type], error_results_dict[noise_type]):
            lower_bound = max(0, mean - std)
            upper_bound = min(1, mean + std)
            print(f"{noise:<15.3f} | {mean:.3f} ± {std:.3f} | [{lower_bound:.3f}, {upper_bound:.3f}]")

    # Mostrar la figura
    plt.show()

    # Guardar resultados con errores
    save_results_to_csv_with_errors(noise_levels, accuracy_results_dict, error_results_dict)




