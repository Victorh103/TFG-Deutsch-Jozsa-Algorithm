import matplotlib.pyplot as plt
import numpy as np
import json

def load_json_data(file_2q='C:/Users/victo/TFG-Computacion cuantica/TFG-Deutsch-Jozsa-Algorithm/Cuantico/Cesga/2qubitscesga.json', file_4q='C:/Users/victo/TFG-Computacion cuantica/TFG-Deutsch-Jozsa-Algorithm/Cuantico/Cesga/4qubitscesga.json'):
    """Carga los datos desde los archivos JSON"""
    
    # Cargar archivo de 2 qubits
    with open(file_2q, 'r', encoding='utf-8') as f:
        raw_2q = json.load(f)
    
    # Cargar archivo de 4 qubits  
    with open(file_4q, 'r', encoding='utf-8') as f:
        raw_4q = json.load(f)
    
    # Procesar datos de 2 qubits
    stats_2q = raw_2q['estadisticas']
    data_2q = {
        'precision_total': stats_2q['precision_total'] * 100,
        'precision_constant': stats_2q['precision_constant'] * 100,
        'precision_balanced': stats_2q['precision_balanced'] * 100,
    }
    
    # Procesar datos de 4 qubits
    stats_4q = raw_4q['estadisticas']
    data_4q = {
        'precision_total': stats_4q['precision']['total'] * 100,
        'precision_constant': stats_4q['precision']['constant'] * 100,
        'precision_balanced': stats_4q['precision']['balanced'] * 100,
    }
    
    return data_2q, data_4q

def create_simple_comparison():
    """Crea una figura simple y limpia"""
    
    # Cargar datos
    data_2q, data_4q = load_json_data()
    
    # Configuración simple
    plt.rcParams.update({
        'font.size': 12,
        'font.family': 'sans-serif'
    })
    
    # Crear figura simple
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Datos
    categorias = ['Constantes', 'Balanceadas', 'Total']
    valores_2q = [data_2q['precision_constant'], data_2q['precision_balanced'], data_2q['precision_total']]
    valores_4q = [data_4q['precision_constant'], data_4q['precision_balanced'], data_4q['precision_total']]
    
    # Posiciones
    x = np.arange(len(categorias))
    width = 0.35
    
    # Barras simples
    bars1 = ax.bar(x - width/2, valores_2q, width, label='2 Qubits', 
                   color='lightblue', edgecolor='black')
    bars2 = ax.bar(x + width/2, valores_4q, width, label='4 Qubits', 
                   color='orange', edgecolor='black')
    
    # Etiquetas básicas
    ax.set_ylabel('Precisión (%)')
    ax.set_title('Algoritmo Deutsch-Jozsa: 2 vs 4 Qubits')
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend()
    
    # Límites del eje Y
    ax.set_ylim(0, 100)
    
    # Valores sobre las barras
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom')
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # Layout ajustado
    plt.tight_layout()
    
    # Guardar
    plt.savefig('deutsch_jozsa_simple.png', dpi=500, bbox_inches='tight')
    
    plt.show()
    
    print("Figura guardada como: deutsch_jozsa_simple.png")

if __name__ == "__main__":
    create_simple_comparison()