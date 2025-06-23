import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

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

# Parámetros
num_trials = 200
rango = range(2, 18)
media = []
error_estandar = []

print("Calculando estadísticas para cada valor de n...")
print("=" * 50)

for n in rango:
    evaluaciones_por_trial = []
    
    # Recopilar todas las evaluaciones para este n
    for _ in range(num_trials):
        if random.random() < 0.5:
            oracle = create_oracle(n, "constante")
            # Para oráculo constante, siempre necesitará 2^(n-1)+1 evaluaciones
            evaluaciones_por_trial.append(2**(n-1) + 1)
        else:
            oracle = create_oracle(n, "balanceado")
            evaluaciones_por_trial.append(deutsch_jozsa_classical(n, oracle))
    
    # Calcular estadísticas
    mean_val = np.mean(evaluaciones_por_trial)
    std_val = np.std(evaluaciones_por_trial, ddof=1)  # ddof=1 para muestra
    se_val = std_val / np.sqrt(num_trials)  # Error estándar
    
    # Guardar resultados
    media.append(mean_val)
    error_estandar.append(se_val)
    
    print(f"n={n:2d}: μ={mean_val:8.2f}, SE={se_val:6.3f}")

print("=" * 50)

# Convertir a arrays numpy para operaciones vectoriales
x = np.array(rango)
y = np.array(media)
std_errors = np.array(error_estandar)

# Ajuste a una función exponencial y = a * 2^(b * x)
# Tomamos log2 de ambos lados: log2(y) = log2(a) + b*x
log_y = np.log2(y)
coeffs = np.polyfit(x, log_y, 1)
b, log_a = coeffs[0], coeffs[1]
a = 2**log_a

# Calcular métricas de calidad
fit_y = a * (2 ** (b * x))

# Coeficiente de determinación (R²)
ss_res = np.sum((y - fit_y) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r_squared = 1 - (ss_res / ss_tot)

# Coeficiente de correlación de Pearson
correlation_matrix = np.corrcoef(y, fit_y)
r_pearson = correlation_matrix[0, 1]

# Chi-cuadrado reducido
degrees_of_freedom = len(x) - 2  # n_points - n_parameters
chi_squared_reduced = ss_res / degrees_of_freedom

# Estadísticas de regresión lineal (en escala log)
slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_y)

# Análisis de la variabilidad
cv_mean = np.mean(std_errors / y) * 100  # Coeficiente de variación promedio con SE

# Imprimir resultados por consola
print("="*60)
print("           ANÁLISIS DEL ALGORITMO DEUTSCH-JOZSA")
print("="*60)
print(f"Ecuación del ajuste exponencial:")
print(f"    y = {a:.4f} × 2^({b:.4f} × n)")
print()
print("COEFICIENTE DE DETERMINACIÓN:")
print("-"*40)
print(f"  R² = {r_squared:.6f}")
print(f"  Varianza explicada: {r_squared*100:.2f}%")
print()
print("OTRAS MÉTRICAS:")
print("-"*40)
print(f"  • Coeficiente de correlación (R):     {r_pearson:.6f}")
print(f"  • Chi-cuadrado reducido (χ²ᵣ):        {chi_squared_reduced:.4f}")
print(f"  • Error estándar del exponente:       ±{std_err:.6f}")
print(f"  • Valor p (significancia):            {p_value:.2e}")
print(f"  • Coeficiente de variación promedio:  {cv_mean:.2f}%")
print()

# Interpretación
if r_squared > 0.99:
    quality = "EXCELENTE"
elif r_squared > 0.95:
    quality = "MUY BUENO"
elif r_squared > 0.90:
    quality = "BUENO"
else:
    quality = "REGULAR"

print(f"CALIDAD DEL AJUSTE: {quality}")
print(f"VARIABILIDAD: {'BAJA' if cv_mean < 10 else 'MODERADA' if cv_mean < 25 else 'ALTA'}")

if p_value < 0.001:
    print("Significancia: ALTAMENTE SIGNIFICATIVO (p < 0.001)")
elif p_value < 0.01:
    print("Significancia: MUY SIGNIFICATIVO (p < 0.01)")
elif p_value < 0.05:
    print("Significancia: SIGNIFICATIVO (p < 0.05)")
else:
    print("Significancia: NO SIGNIFICATIVO (p ≥ 0.05)")

print("="*60)

# Gráfica académica profesional con barras de error
plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})
fig, ax = plt.subplots(figsize=(10, 7))

# Datos experimentales con barras de error (desviación estándar)
ax.errorbar(rango, media, yerr=std_err, fmt='o', color='blue', 
            markersize=6, markerfacecolor='lightblue', markeredgecolor='blue', 
            markeredgewidth=1, ecolor='red', elinewidth=2.5, capsize=0,
            label="Datos experimentales ± σ")

# Línea de ajuste
x_smooth = np.linspace(min(rango), max(rango), 100)
fit_y_smooth = a * (2 ** (b * x_smooth))
ax.plot(x_smooth, fit_y_smooth, '-', color='red', linewidth=2, 
        label=f'Ajuste: y = {a:.2f} × 2$^{{{b:.3f}n}}$')

# Configuración de la escala logarítmica
ax.set_yscale("log", base=2)

# Etiquetas y título académicos
ax.set_xlabel("Número de bits (n)", fontsize=14)
ax.set_ylabel("Logaritmo del Número de evaluaciones", fontsize=14)
ax.set_title("Algoritmo Deutsch-Jozsa Clásico", 
             fontsize=16, pad=20)

# Grilla simple y profesional
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8)
ax.grid(True, alpha=0.15, linestyle='-', linewidth=0.3, which='minor')

# Leyenda académica
ax.legend(fontsize=12, loc='upper left', frameon=True)

# Configuración de los ticks
ax.tick_params(axis='both', which='major', labelsize=11)

# Configuración del eje X - todos los valores
ax.set_xticks(rango)
ax.set_xlim(min(rango)-0.5, max(rango)+0.5)

# Fondo blanco limpio
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

plt.tight_layout()
plt.show()