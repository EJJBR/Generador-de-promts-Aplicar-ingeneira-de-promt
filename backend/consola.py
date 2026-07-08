"""
Demo de consola - Generador de Prompts

Uso:
    python consola.py

Escribe una consulta de estadística como la haría un estudiante,
y el sistema devuelve: tema, nivel, IA recomendada y el prompt optimizado.

Escribe "salir" para terminar.
"""

from app.services.clasificador import clasificar_consulta


def mostrar_resultado(resultado: dict):
    print("\n" + "=" * 60)
    print(f"  Tema:            {resultado.get('tema')}")
    print(f"  Nivel:           {resultado.get('nivel')}")
    print(f"  IA recomendada:  {resultado.get('ia_recomendada')}")
    print(f"  Justificación:   {resultado.get('justificacion')}")
    print("-" * 60)
    print("  Prompt optimizado (cópialo y pégalo en la IA recomendada):")
    print()
    print(f"  {resultado.get('prompt_optimizado')}")
    print("=" * 60 + "\n")


def main():
    print("=" * 60)
    print("  GENERADOR DE PROMPTS - Demo de consola")
    print("  Escribe tu consulta de estadística (o 'salir' para terminar)")
    print("=" * 60)

    while True:
        consulta = input("\nTu consulta: ").strip()

        if consulta.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego!")
            break

        if not consulta:
            print("Por favor escribe una consulta.")
            continue

        try:
            print("\nProcesando...")
            resultado = clasificar_consulta(consulta)
            mostrar_resultado(resultado)
        except ValueError as e:
            print(f"\n[ERROR] {e}")
        except Exception as e:
            print(f"\n[ERROR inesperado] {e}")


if __name__ == "__main__":
    main()