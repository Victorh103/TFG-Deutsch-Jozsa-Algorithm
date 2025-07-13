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
        evaluations += 1
        if oracle(x) != first_output:
            return evaluations  # Encuentro diferencia: es balanceado
    
    return evaluations  # No hay diferencias: es constante

# Parámetros del experimento
n = 16
total_trials = 6000  
num_trials_balanced = total_trials // 2  # 50% balanceadas
num_trials_constant = total_trials // 2  # 50% constantes

print("="*60)
print(f"    ANÁLISIS HISTOGRAMA DEUTSCH-JOZSA (n = {n} bits)")
print("="*60)

evaluations_balanced = []
evaluations_constant = []

# Crear lista de tipos mezclados aleatoriamente (50% cada uno)
oracle_types = (['balanceado'] * num_trials_balanced + 
                ['constante'] * num_trials_constant)
random.shuffle(oracle_types)  # Mezclar aleatoriamente el orden

print(f"Ejecutando {total_trials} experimentos con mezcla equilibrada...")

# Realizar todos los experimentos mezclados
for trial, oracle_type in enumerate(oracle_types):
    oracle = create_oracle(n, oracle_type)
    evaluations = deutsch_jozsa_classical(n, oracle)
    
    # Separar resultados por tipo para mantener colores diferenciados
    if oracle_type == "balanceado":
        evaluations_balanced.append(evaluations)
    else:
        evaluations_constant.append(evaluations)
    
    # Mostrar progreso cada 1000 iteraciones
    if (trial + 1) % 1000 == 0:
        balanced_count = len(evaluations_balanced)
        constant_count = len(evaluations_constant)
        print(f"Progreso: {trial + 1}/{total_trials} experimentos completados")
        print(f"  - Balanceadas: {balanced_count}, Constantes: {constant_count}")

# Verificar la mezcla equilibrada
print(f"\nRESULTADO DE LA MEZCLA:")
print(f"  - Funciones balanceadas: {len(evaluations_balanced)} ({len(evaluations_balanced)/total_trials*100:.1f}%)")
print(f"  - Funciones constantes: {len(evaluations_constant)} ({len(evaluations_constant)/total_trials*100:.1f}%)")

# Configuración de matplotlib para estilo académico
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.linewidth': 1,
    'grid.alpha': 0.3
})

# Crear histograma con probabilidades
fig, ax = plt.subplots(figsize=(12, 8))

# Rango de evaluaciones posibles (de 2 a n//2 + 1)
max_eval_possible = n//2 + 1
eval_range = range(2, max_eval_possible + 1)

# Calcular probabilidades para cada número de evaluaciones
prob_balanced = []
prob_constant = []

for num_eval in eval_range:
    count_balanced = evaluations_balanced.count(num_eval)
    count_constant = evaluations_constant.count(num_eval)
    
    prob_balanced.append(count_balanced / total_trials)
    prob_constant.append(count_constant / total_trials)

# Crear las barras centradas en 2, 3, 4, etc.
x_positions = np.array(eval_range)
width = 0.4

# Plotear las barras manteniendo los colores originales diferenciados
bars1 = ax.bar(x_positions - width/2, prob_balanced, width, 
               label=f'Funciones balanceadas', 
               color='steelblue', alpha=0.7, 
               edgecolor='black', linewidth=0.8)

bars2 = ax.bar(x_positions + width/2, prob_constant, width,
               label=f'Funciones constantes', 
               color='red', alpha=0.7,
               edgecolor='black', linewidth=0.8)

# Etiquetas y título
ax.set_xlabel("Número de evaluaciones", fontsize=14)
ax.set_ylabel("Probabilidad", fontsize=14)
ax.set_title(f"Función que presenta m = {n} posibles entradas", 
             fontsize=16, pad=20)

# Configuración de ejes - empezar desde 2 evaluaciones
ax.set_xlim(0, n +1)
ax.set_xticks(range(1, n+1))
max_prob = max(max(prob_balanced), max(prob_constant))
ax.set_ylim(0, 1)

# Agregar leyenda
ax.legend(fontsize=12, loc='upper right')

# Grid
ax.grid(axis='y', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.show()

# Estadísticas descriptivas
print("\n" + "="*60)
print("ESTADÍSTICAS DESCRIPTIVAS - MEZCLA EQUILIBRADA")
print("="*60)

print(f"\nFUNCIONES BALANCEADAS ({len(evaluations_balanced)} experimentos):")
print(f"  Media de evaluaciones: {np.mean(evaluations_balanced):.2f}")
print(f"  Desviación estándar: {np.std(evaluations_balanced):.2f}")
print(f"  Mínimo: {min(evaluations_balanced)}")
print(f"  Máximo: {max(evaluations_balanced)}")

print(f"\nFUNCIONES CONSTANTES ({len(evaluations_constant)} experimentos):")
print(f"  Media de evaluaciones: {np.mean(evaluations_constant):.2f}")
print(f"  Desviación estándar: {np.std(evaluations_constant):.2f}")
print(f"  Mínimo: {min(evaluations_constant)}")
print(f"  Máximo: {max(evaluations_constant)}")

# Estadísticas comparativas
print(f"\nCOMPARACIÓN ESTADÍSTICA:")
print(f"  Ratio de medias (balanceado/constante): {np.mean(evaluations_balanced)/np.mean(evaluations_constant):.2f}")
print(f"  Diferencia de medias: {np.mean(evaluations_balanced) - np.mean(evaluations_constant):.2f}")

print("\n" + "="*60)