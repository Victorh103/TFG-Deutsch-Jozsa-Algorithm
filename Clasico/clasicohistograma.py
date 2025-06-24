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
n = 16
num_trials = 5000  

print("="*60)
print(f"    ANÁLISIS HISTOGRAMA DEUTSCH-JOZSA (n = {n} bits)")
print("="*60)

evaluations_list = []

# Realizar experimentos solo con oráculos balanceados
for trial in range(num_trials):
    oracle = create_oracle(n, "balanceado")
    evaluations = deutsch_jozsa_classical(n, oracle)
    evaluations_list.append(evaluations)
    
    # Mostrar progreso cada 200 iteraciones
    if (trial + 1) % 200 == 0:
        print(f"Progreso: {trial + 1}/{num_trials} experimentos completados")


# Configuración de matplotlib para estilo académico
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.linewidth': 1,
    'grid.alpha': 0.3
})

# Histograma figura
fig, ax = plt.subplots(figsize=(12, 8))

max_eval_possible = n//2 + 1
bins = np.arange(0.5, n + 1.5, 1)

counts, bin_edges, patches = ax.hist(evaluations_list, bins=bins, 
                                   edgecolor='black', linewidth=0.8, 
                                   alpha=0.7, color='steelblue',
                                   density=False)

# Etiquetas y título
ax.set_xlabel("Número de evaluaciones del oráculo", fontsize=14)
ax.set_ylabel("Frecuencia", fontsize=14)
ax.set_title(f"Algoritmo Deutsch-Jozsa Clasico\n (n = {n} bits, {num_trials} experimentos)", 
             fontsize=16, pad=20)

# Configuración de ejes
ax.set_xlim(0.5, n + 0.5)
ax.set_xticks(range(1, n + 1))
ax.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()

print("\n" + "="*60)