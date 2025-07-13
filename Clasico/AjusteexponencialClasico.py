import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

def create_oracle(n, type="balanceado"):
    """Crea el oráculo."""
    if type == "constante":
        output = random.choice([0, 1])
        return lambda x: output
    elif type == "balanceado":
        values = [0] * (2**(n-1)) + [1] * (2**(n-1))    # Mitad 0 y mitad 1
        random.shuffle(values)  # Mezclar los valores
        mapping = {i: values[i] for i in range(2**n)}
        return lambda x: mapping[x]

def deutsch_jozsa_classical(n, oracle):
    evaluations = 1
    first_output = oracle(0)
    
    for x in range(1, 2**(n-1)+1):
        if oracle(x) != first_output:
            return evaluations
        evaluations += 1
    
    return evaluations

# Función de ajuste: y = a * 2^n
def exponential_func(n, a):
    return a * (2 ** n)

# Parámetros
num_trials = 200
rango = range(2, 20)
media = []
error_estandar = []

print("Calculando estadísticas para cada valor de n...")
print("=" * 50)

for n in rango:
    evaluaciones_por_trial = []
    
    for _ in range(num_trials):
        if random.random() < 0.5:
            oracle = create_oracle(n, "constante")
            evaluaciones_por_trial.append(2**(n-1) + 1)
        else:
            oracle = create_oracle(n, "balanceado")
            evaluaciones_por_trial.append(deutsch_jozsa_classical(n, oracle))
    
    mean_val = np.mean(evaluaciones_por_trial)
    std_val = np.std(evaluaciones_por_trial, ddof=1)  
    se_val = std_val / np.sqrt(num_trials)  
    
    # Guardar resultados
    media.append(mean_val)
    error_estandar.append(se_val)
    
    print(f"n={n:2d}: μ={mean_val:8.2f}, SE={se_val:6.3f}")

print("=" * 50)

x = np.array(rango)
y = np.array(media)
std_errors = np.array(error_estandar)

# AJUSTE: y = a * 2^n
popt, pcov = curve_fit(exponential_func, x, y)
a = popt[0]
a_error = np.sqrt(np.diag(pcov))[0]

# Calcular valores ajustados
fit_y = exponential_func(x, a)

# Coeficiente de determinación (R²)
ss_res = np.sum((y - fit_y) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r_squared = 1 - (ss_res / ss_tot)

# Coeficiente de Pearson
correlation_matrix = np.corrcoef(y, fit_y)
r_pearson = correlation_matrix[0, 1]

# Análisis de la variabilidad
cv_mean = np.mean(std_errors / y) * 100

print("="*60)
print("           ANÁLISIS DEL ALGORITMO DEUTSCH-JOZSA")
print("="*60)
print(f"Ecuación del ajuste:")
print(f"    y = {a:.6f} × 2^n")
print(f"    Error en 'a': ±{a_error:.6f}")
print()
print(f"Coeficiente de determinación (R²): {r_squared:.4f}")
print(f"Coeficiente de correlación de Pearson: {r_pearson:.4f}")
print(f"Coeficiente de variación promedio (CV): {cv_mean:.2f}%")

# Gráfica
plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})
fig, ax = plt.subplots(figsize=(10, 7))

# Datos experimentales con barras de error
ax.errorbar(rango, media, yerr=3*std_errors, fmt='o', color='blue', 
            markersize=6, markerfacecolor='lightblue', markeredgecolor='blue', 
            markeredgewidth=0.7, ecolor='red', elinewidth=2.5, capsize=0,
            label="Datos experimentales ± 3σ")

# Línea de ajuste
x_smooth = np.linspace(min(rango), max(rango), 100)
fit_y_smooth = exponential_func(x_smooth, a)
ax.plot(x_smooth, fit_y_smooth, '-', color='red', linewidth=2, 
        label=f'Ajuste: y = {a:.4f} × 2$^n$')

# Escala logarítmica
ax.set_yscale("log", base=2)

# Etiquetas y título académicos
ax.set_xlabel("Número de bits (n)", fontsize=14)
ax.set_ylabel("Número de evaluaciones", fontsize=14)
ax.set_title("Algoritmo Deutsch-Jozsa Clásico", 
             fontsize=16, pad=20)
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8)
ax.grid(True, alpha=0.15, linestyle='-', linewidth=0.3, which='minor')

ax.legend(fontsize=12, loc='upper left', frameon=True)

ax.tick_params(axis='both', which='major', labelsize=11)

ax.set_xticks(rango)
ax.set_xlim(min(rango)-0.5, max(rango)+0.5)

# Fondo blanco 
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

plt.tight_layout()
plt.show()