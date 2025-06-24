# TFG-Deutsch-Jozsa-Algorithm

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Qiskit](https://img.shields.io/badge/Qiskit-0.45+-purple.svg)](https://qiskit.org/)
[![Status](https://img.shields.io/badge/Status-Uncomplete-success.svg)]()

## 🎯 Resumen 

En este TFG se realiza un análisis exhaustivo del algoritmo Deutsch-Jozsa, uno de los primeros algoritmos que demostró una ventaja computacional cuántica. A través de implementaciones clásicas, simulaciones cuánticas y validación experimental en hardware real, este proyecto explora las fronteras entre la computación clásica y cuántica.

**Resultado clave**: Demostración de ventaja cuántica exponencial (O(2^n) → O(1)) con análisis del impacto del ruido cuántico en sistemas reales.

---

## 📋 Índice

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Resultados Principales](#-resultados-principales)
- [Instalación](#-instalación)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Metodología](#-metodología)
- [Validación Experimental](#-validación-experimental)
- [Limitaciones y Trabajo Futuro](#-limitaciones-y-trabajo-futuro)

---

## 🔬 Descripción del Proyecto

### Problema de Deutsch-Jozsa

Dado un oráculo que implementa una función booleana f: {0,1}^n → {0,1}, determinar si la función es:

- **Constante**: f(x) = c para todo x (donde c ∈ {0,1})
- **Balanceada**: f(x) = 0 para exactamente la mitad de las entradas

### Objetivos de Investigación

1. **Análisis Teórico**: Comparar complejidades temporales clásica O(2^(n-1)+1) vs. cuántica O(1)  
2. **Implementación Práctica**: Desarrollar simulaciones en Qiskit para sistemas de 2-6 qubits  
3. **Análisis de Ruido**: Evaluar degradación de fidelidad bajo tres modelos de ruido cuántico  
4. **Validación Experimental**: Verificar resultados en hardware cuántico real (IBM Quantum vía CESGA)

---

## 📊 Resultados Principales

### 🏛️ Análisis Clásico

- Complejidad Temporal: O(2^(n-1) + 1)  
- Ajuste Exponencial: R² = 0.9998 (n ∈ [2,18])  
- Ecuación: y = 2.47 × 2^(0.998n)  
- Significancia: p < 0.001

### ⚛️ Análisis Cuántico Ideal

- Complejidad Temporal: O(1)  
- Fidelidad: 100% (simulación perfecta)  
- Evaluaciones del Oráculo: 1 (independiente de n)  
- Ventaja Exponencial: Factor 2^(n-1)

### 🌊 Análisis de Ruido

| Modelo de Ruido  | Umbral 50% Fidelidad | Umbral 75% Fidelidad |
|------------------|----------------------|-----------------------|
| Despolarización  | p = 0.245            | p = 0.087             |
| Decoherencia     | p = 0.198            | p = 0.062             |
| Decaimiento      | p = 0.167            | p = 0.053             |

### 🖥️ Resultados en Hardware Real (CESGA)

| Sistema    | Constantes | Balanceadas | Precisión Total |
|------------|------------|-------------|-----------------|
| 2 Qubits   | 96.0%      | 48.7%       | 60.5%           |
| 4 Qubits   | 40.0%      | 89.6%       | 81.3%           |
| **Mejora General** |        |             | **+20.8%**       |

---

## 🚀 Instalación

### Requisitos del Sistema

- Python 3.8 o superior  
- 8GB RAM mínimo (16GB recomendado para n>4)  
- Acceso a internet para IBM Quantum

### Instalación Rápida

```bash
git clone https://github.com/tu-usuario/deutsch-jozsa-tfg.git
cd deutsch-jozsa-tfg
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

#### Dependencias

```
qiskit>=0.45.0  
qiskit-aer>=0.13.0  
qiskit-ibm-runtime>=0.15.0  
numpy>=1.21.0  
matplotlib>=3.5.0  
scipy>=1.7.0  
pandas>=1.3.0  
tqdm>=4.62.0  
seaborn>=0.11.0
```

---

## 📂 Estructura del Proyecto

```
TFG-Deutsch-Jozsa-Algorithm/
├── src/
│   ├── classical/
│   │   ├── AjusteexponencialClasico.py
│   │   └── clasicohistograma.py
│   ├── quantum/
│   │   ├── Deutsch_Jozsa_Qiskit.py
│   │   ├── 4_qubits.py
│   │   └── 6_qubits.py
│   ├── noise_analysis/
│   │   ├── Analisismodelosruido.py
│   │   └── Grafico_ruido_vs_fidelidad.py
│   └── utils/
│       ├── oracle_builder.py
│       ├── noise_models.py
│       └── visualization.py
├── results/
│   ├── figures/
│   ├── data/
│   └── cesga/
├── docs/
│   ├── teoria_deutsch_jozsa.md
│   ├── metodologia.md
│   └── referencias/
├── tests/
│   ├── test_classical.py
│   ├── test_quantum.py
│   └── test_noise.py
├── requirements.txt
├── config.yaml
└── README.md
```

---

## 🧪 Metodología

### Algoritmo Clásico

1. Estrategia Determinística: Evaluación secuencial hasta encontrar diferencia  
2. Complejidad Peor Caso: 2^(n-1) + 1 evaluaciones  
3. Análisis Estadístico: 200 experimentos por valor de n ∈ [2,18]  
4. Métricas: Ajuste exponencial, R², chi-cuadrado

### Algoritmo Cuántico

1. Preparación: |0⟩^⊗n |1⟩ → superposición uniforme  
2. Evaluación Oráculo: Una aplicación de U_f  
3. Interferencia: Hadamards finales + medición  
4. Criterio: |00...0⟩ → constante, ortogonal → balanceada

---

## 🔉 Modelos de Ruido

### Modelo de Despolarización
```python
noise_model.add_all_qubit_quantum_error(
    depolarizing_error(p, 1), ['h', 'x', 'z']
)
```

### Modelo de Decoherencia de Fase
```python
noise_model.add_all_qubit_quantum_error(
    phase_damping_error(p), ['h', 'x', 'z']
)
```

### Modelo de Decaimiento de Amplitud
```python
noise_model.add_all_qubit_quantum_error(
    amplitude_damping_error(p), ['h', 'x', 'z']
)
```

---

## 🔭 Limitaciones y Trabajo Futuro

### Limitaciones Actuales

1. **Escalabilidad Clásica**: Simulaciones limitadas a n ≤ 18 por recursos computacionales  
2. **Ruido Simplificado**: Modelos académicos vs. ruido real complejo  
3. **Hardware Limitado**: Acceso restringido a sistemas de >27 qubits  
4. **Correlaciones**: No considera efectos de correlación temporal del ruido

### Trabajo Futuro Propuesto

1. **Extensión a n>10**: Implementación en supercomputadores  
2. **Ruido Realista**: Modelos basados en calibraciones experimentales  
3. **Corrección de Errores**: Implementación de códigos cuánticos
