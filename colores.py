#-----------colores de texto 
def color(c):
    colores = {
        "naranja": "\033[38;5;208m",
        "amarillo": "\033[33m",
        "verde": "\033[32m",
        "rojo": "\033[31m",
        "..": "\033[0m"
    }
    return colores.get(c, "")


