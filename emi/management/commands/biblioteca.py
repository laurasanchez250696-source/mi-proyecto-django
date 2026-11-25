from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from emi.services import BibliotecaService


class Command(BaseCommand):
    help = "Inicia el sistema interactivo de reserva de libros de la biblioteca"

    def handle(self, *args, **options):
        while True:
            print("\n=============================")
            print(" BIBLIOTECA")
            print("=============================")
            print("1. Registrar libro")
            print("2. Registrar socio")
            print("3. Listar libros")
            print("4. Buscar libro")
            print("5. Listar socios")
            print("6. Realizar reserva")
            print("7. Cancelar reserva")
            print("8. Retirar libro reservado")
            print("9. Devolver libro")
            print("10. Listar reservas de un socio")
            print("11. Listar todas las reservas")
            print("12. Consultas especiales (ORM)")
            print("0. Salir")
            print("=============================")

            opcion = input("Seleccione una opción: ").strip()

            try:
                if opcion == "1":
                    self.registrar_libro()
                elif opcion == "2":
                    self.registrar_socio()
                elif opcion == "3":
                    self.listar_libros()
                elif opcion == "4":
                    self.buscar_libro()
                elif opcion == "5":
                    self.listar_socios()
                elif opcion == "6":
                    self.realizar_reserva()
                elif opcion == "7":
                    self.cancelar_reserva()
                elif opcion == "8":
                    self.retirar_libro()
                elif opcion == "9":
                    self.devolver_libro()
                elif opcion == "10":
                    self.listar_reservas_socio()
                elif opcion == "11":
                    self.listar_todas_reservas()
                elif opcion == "12":
                    self.menu_consultas()
                elif opcion == "0":
                    print("Saliendo del sistema...")
                    break
                else:
                    print("Error: Opción inválida. Intente nuevamente.")
            except ValidationError as e:
                if hasattr(e, "messages"):
                    for msg in e.messages:
                        print(f"Error de validación: {msg}")
                else:
                    print(f"Error de validación: {e}")
            except ValueError:
                print("Error: Debe ingresar un valor numérico válido.")
            except Exception as e:
                print(f"Error inesperado: {e}")

    def registrar_libro(self):
        print("\n--- Registrar Libro ---")
        isbn = input("ISBN: ").strip()
        titulo = input("Título: ").strip()
        autor = input("Autor: ").strip()
        anio = int(input("Año de publicación: ").strip())
        cantidad = int(input("Cantidad total de ejemplares: ").strip())

        libro = BibliotecaService.registrar_libro(isbn, titulo, autor, anio, cantidad)
        print(f"Libro registrado con éxito: {libro}")

    def registrar_socio(self):
        print("\n--- Registrar Socio ---")
        numero = int(input("Número de socio: ").strip())
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        dni = input("DNI: ").strip()
        email = input("Email: ").strip()
        estado_in = input("¿Está activo? (s/n) [s]: ").strip().lower()
        activo = False if estado_in == "n" else True

        socio = BibliotecaService.registrar_socio(numero, nombre, apellido, dni, email, activo)
        print(f"Socio registrado con éxito: {socio}")

    def listar_libros(self):
        print("\n--- Listado de Libros ---")
        libros = BibliotecaService.listar_libros()
        if not libros:
            print("No hay libros registrados.")
            return
        for libro in libros:
            print(f" - {libro}")

    def buscar_libro(self):
        print("\n--- Buscar Libro ---")
        criterio = input("Ingrese ISBN, Título o Autor (o parte del texto): ").strip()
        resultados = BibliotecaService.buscar_libros(criterio)
        if not resultados:
            print("No se encontraron libros con ese criterio.")
            return
        for libro in resultados:
            print(f" - {libro}")

    def listar_socios(self):
        print("\n--- Listado de Socios ---")
        socios = BibliotecaService.listar_socios()
        if not socios:
            print("No hay socios registrados.")
            return
        for socio in socios:
            print(f" - {socio}")

    def realizar_reserva(self):
        print("\n--- Realizar Reserva ---")
        numero_socio = int(input("Número de socio: ").strip())
        isbn = input("ISBN del libro: ").strip()
        reserva = BibliotecaService.realizar_reserva(numero_socio, isbn)
        print(f"Reserva creada con éxito: {reserva}")

    def cancelar_reserva(self):
        print("\n--- Cancelar Reserva ---")
        reserva_id = int(input("ID de la reserva a cancelar: ").strip())
        reserva = BibliotecaService.cancelar_reserva(reserva_id)
        print(f"Reserva cancelada con éxito: {reserva}")

    def retirar_libro(self):
        print("\n--- Retirar Libro Reservado ---")
        reserva_id = int(input("ID de la reserva a retirar: ").strip())
        reserva = BibliotecaService.retirar_libro(reserva_id)
        print(f"Libro retirado con éxito: {reserva}")

    def devolver_libro(self):
        print("\n--- Devolver Libro ---")
        reserva_id = int(input("ID de la reserva a devolver: ").strip())
        reserva = BibliotecaService.devolver_libro(reserva_id)
        print(f"Libro devuelto y reserva finalizada: {reserva}")

    def listar_reservas_socio(self):
        print("\n--- Reservas de un Socio ---")
        numero_socio = int(input("Número de socio: ").strip())
        reservas = BibliotecaService.listar_reservas_socio(numero_socio)
        if not reservas:
            print("El socio no tiene reservas registradas.")
            return
        for r in reservas:
            print(f" - {r} | Fecha: {r.fecha_reserva.strftime('%d/%m/%Y %H:%M')}")

    def listar_todas_reservas(self):
        print("\n--- Todas las Reservas ---")
        reservas = BibliotecaService.listar_todas_reservas()
        if not reservas:
            print("No hay reservas registradas.")
            return
        for r in reservas:
            print(f" - {r} | Fecha: {r.fecha_reserva.strftime('%d/%m/%Y %H:%M')}")

    def menu_consultas(self):
        print("\n--- Consultas ORM ---")
        print("1. Libros disponibles")
        print("2. Libros sin ejemplares disponibles")
        print("3. Reservas pendientes")
        print("4. Reservas de un libro (por ISBN)")
        print("5. Socios activos")
        sub = input("Seleccione consulta: ").strip()

        if sub == "1":
            for l in BibliotecaService.libros_disponibles():
                print(f" - {l}")
        elif sub == "2":
            for l in BibliotecaService.libros_agotados():
                print(f" - {l}")
        elif sub == "3":
            for r in BibliotecaService.reservas_pendientes():
                print(f" - {r}")
        elif sub == "4":
            isbn = input("ISBN del libro: ").strip()
            for r in BibliotecaService.reservas_por_libro(isbn):
                print(f" - {r}")
        elif sub == "5":
            for s in BibliotecaService.socios_activos():
                print(f" - {s}")
        else:
            print("Opción de consulta inválida.")