# Proyecto 2: Calculadora IP — CIDR y VLSM

Aplicación web desarrollada en **Python (Flask)** para realizar cálculos de direccionamiento IPv4 mediante **CIDR** (*Classless Inter-Domain Routing*) y diseño de subredes de tamaño variable mediante **VLSM** (*Variable Length Subnet Mask*).

---

## Enlaces del Proyecto

* **Aplicación en línea (Render):** `https://[tu-servicio].onrender.com`
* **Repositorio en GitHub:** `https://github.com/[tu-usuario]/EquipoX_CalculadoraIP`
* **Video explicativo:** `https://youtu.be/[enlace-no-listado]`

---

## Integrantes y Roles del Equipo

* **Cruz Guzman Carlos Alberto**
* **Magaña Fierro Elka Natalia**
* **Romero Ortega Israel**

---

## Funcionalidades Principales

1. **Calculadora IP (CIDR):**
   * Acepta direcciones en formato `IP/prefijo` (ej. `192.168.10.0/24`) o `IP` + máscara decimal/prefijo por separado.
   * Calcula dirección de red, máscara en decimal punteado y prefijo `/n`, primer host, último host, dirección de broadcast, cantidad de hosts disponibles y representación binaria de 32 bits.
2. **Calculadora IP (VLSM):**
   * Recibe una red base en notación CIDR y una lista dinámica de subredes con sus hosts requeridos.
   * Ordena las subredes de mayor a menor demanda, asigna bloques contiguos sin solapamientos, calcula hosts válidos y espacio desperdiciado, e informa las direcciones restantes de la red base.
   * Valida entradas y detecta cuando la red base carece de espacio suficiente.

---

## Estructura del Proyecto

```text
EquipoX_CalculadoraIP/
├── core/
│   ├── __init__.py
│   └── calculators.py       # Lógica matemática CIDR y VLSM (operaciones bitwise)
├── templates/
│   └── index.html           # Interfaz web principal
├── static/
│   ├── style.css            # Estilos de la interfaz
│   └── app.js               # Consumo de API con Fetch y renderizado dinámico
├── tests/
│   └── test_calculators.py  # Pruebas unitarias automatizadas
├── app.py                   # Servidor web y API REST en Flask
├── requirements.txt         # Dependencias del proyecto
├── ejecutar_local.bat       # Ejecutable automático para Windows
├── ejecutar_local.sh        # Ejecutable automático para Linux/macOS
└── README.md                # Documentación del repositorio
