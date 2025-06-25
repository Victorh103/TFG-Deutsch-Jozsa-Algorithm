import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def create_oracle(n, type="balanceado"):
    """
    Crea un oráculo para el algoritmo Deutsch-Jozsa.
    
    Args:
        n: número de bits de entrada
        type: "constante" o "balanceado"
    
    Returns:
        función oráculo
    """
    if type == "constante":
        output = random.choice([0, 1])
        return lambda x: output  
    elif type == "balanceado":
        values = [0] * (2**(n-1)) + [1] * (2**(n-1))  # Mitad 0, mitad 1
        random.shuffle(values)  # Mezclar aleatoriamente
        mapping = {i: values[i] for i in range(2**n)}
        return lambda x: mapping[x]

def deutsch_jozsa_classical(n, oracle):
    """
    Implementación clásica del algoritmo Deutsch-Jozsa.
    
    Args:
        n: número de bits
        oracle: función oráculo
    
    Returns:
        número de evaluaciones necesarias
    """
    evaluations = 1
    first_output = oracle(0)
    
    for x in range(1, n//2 + 1):
        if oracle(x) != first_output:
            return evaluations  # Encuentro diferencia: es balanceado
        evaluations += 1
    
    return evaluations  # Entonces es constante

# Parámetros del experimento
n = 18
num_trials_balanced = 5000
num_trials_constant = 500

print("="*60)
print(f"    ANÁLISIS HISTOGRAMA DEUTSCH-JOZSA (n = {n} bits)")
print("="*60)

evaluations_balanced = []
evaluations_constant = []

# Realizar experimentos con oráculos balanceados
print("Ejecutando experimentos con funciones balanceadas...")
for trial in range(num_trials_balanced):
    oracle = create_oracle(n, "balanceado")
    evaluations = deutsch_jozsa_classical(n, oracle)
    evaluations_balanced.append(evaluations)
    
    # Mostrar progreso cada 1000 iteraciones
    if (trial + 1) % 1000 == 0:
        print(f"Progreso balanceadas: {trial + 1}/{num_trials_balanced} experimentos completados")

# Realizar experimentos con oráculos constantes
print("Ejecutando experimentos con funciones constantes...")
for trial in range(num_trials_constant):
    oracle = create_oracle(n, "constante")
    evaluations = deutsch_jozsa_classical(n, oracle)
    evaluations_constant.append(evaluations)
    
    # Mostrar progreso cada 100 iteraciones
    if (trial + 1) % 100 == 0:
        print(f"Progreso constantes: {trial + 1}/{num_trials_constant} experimentos completados")

# Configuración de matplotlib para estilo académico
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.linewidth': 1,
    'grid.alpha': 0.3
})

# Crear histograma con probabilidades
fig, ax = plt.subplots(figsize=(12, 8))

max_eval_possible = n//2 + 1
bins = np.arange(0.5, max_eval_possible + 1.5, 1)

# Histograma para funciones balanceadas (normalizado para obtener probabilidades)
counts_balanced, bin_edges_balanced = np.histogram(evaluations_balanced, bins=bins)
probabilities_balanced = counts_balanced / num_trials_balanced

# Histograma para funciones constantes (normalizado para obtener probabilidades)
counts_constant, bin_edges_constant = np.histogram(evaluations_constant, bins=bins)
probabilities_constant = counts_constant / num_trials_constant

# Crear las barras
bin_centers = (bin_edges_balanced[:-1] + bin_edges_balanced[1:]) / 2
width = 1  # Ancho de las barras

# Plotear las barras
bars1 = ax.bar(bin_centers - width/2, probabilities_balanced, width, 
               label='Funciones balanceadas', color='steelblue', alpha=0.7, 
               edgecolor='black', linewidth=0.8)

bars2 = ax.bar(bin_centers + width/2, probabilities_constant, width,
               label='Funciones constantes', color='red', alpha=0.7,
               edgecolor='black', linewidth=0.8)

# Etiquetas y título
ax.set_xlabel("Número de evaluaciones", fontsize=14)
ax.set_ylabel("Probabilidad", fontsize=14)
ax.set_title(f"Algoritmo Deutsch-Jozsa Clásico n = {n} bits", 
             fontsize=16, pad=20)

# Configuración de ejes
ax.set_xlim(0, n)
ax.set_xticks(range(1, n+1))
ax.set_ylim(0, max(max(probabilities_balanced), max(probabilities_constant)) * 1.1)

# Agregar leyenda
ax.legend(fontsize=12, loc='upper right')

# Grid
ax.grid(axis='y', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.show()

# Estadísticas descriptivas
print("\n" + "="*60)
print("ESTADÍSTICAS DESCRIPTIVAS")
print("="*60)

print(f"\nFUNCIONES BALANCEADAS ({num_trials_balanced} experimentos):")
print(f"  Media de evaluaciones: {np.mean(evaluations_balanced):.2f}")
print(f"  Desviación estándar: {np.std(evaluations_balanced):.2f}")
print(f"  Mínimo: {min(evaluations_balanced)}")
print(f"  Máximo: {max(evaluations_balanced)}")

print(f"\nFUNCIONES CONSTANTES ({num_trials_constant} experimentos):")
print(f"  Media de evaluaciones: {np.mean(evaluations_constant):.2f}")
print(f"  Desviación estándar: {np.std(evaluations_constant):.2f}")
print(f"  Mínimo: {min(evaluations_constant)}")
print(f"  Máximo: {max(evaluations_constant)}")

print("\n" + "="*60)