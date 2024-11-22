import tkinter as tk
from tkinter import messagebox

# Funcion para escribir en el archivo de bitacora
def write_to_log(message):
    with open("bitacora.txt", "a") as log_file:
        log_file.write(message + "\n")

# Decoradores para AOP
def transaction(func):
    def wrapper(*args, **kwargs):
        write_to_log("[Transaccion] Inicio")
        try:
            result = func(*args, **kwargs)
            write_to_log("[Transaccion] Confirmada")
            return result
        except Exception as e:
            write_to_log("[Transaccion] Deshecha")
            write_to_log(f"Error: {e}")
            raise e
    return wrapper

def audit(action):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            user_id = args[1]
            write_to_log(f"[Log] Accion: {action}, Usuario ID: {user_id}")
            return result
        return wrapper
    return decorator

def validate(func):
    """Aspecto para validar datos de usuario con bitácora."""
    def wrapper(*args, **kwargs):
        self = args[0]  # Referencia a la instancia
        user_id = args[1]  # El primer argumento después de `self` es el ID
        user_data = args[2]  # El segundo argumento posicional es `user_data`
        
        # Validar el nombre y correo
        if not user_data.get("name") or not user_data.get("email"):
            message = f"Error: El nombre y el correo son obligatorios. Usuario ID: {user_id}"
            write_to_log(message)
            raise ValueError(message)
        
        # Validar si el usuario ya existe
        if user_id in self.users:
            message = f"Error: El usuario con ID {user_id} ya existe."
            write_to_log(message)
            raise ValueError(message)
        
        return func(*args, **kwargs)
    return wrapper

# Clase de gestion de usuarios
class UserService:
    def __init__(self):
        self.users = {}

    @transaction
    @audit("Crear")
    @validate
    def create_user(self, user_id, user_data):
        self.users[user_id] = user_data
        write_to_log(f"Usuario creado: {user_id}, Datos: {user_data}")

    @transaction
    @audit("Eliminar")
    def delete_user(self, user_id):
        if user_id not in self.users:
            message = f"Error: El usuario con ID {user_id} no existe."
            write_to_log(message)
            raise ValueError(message)
        del self.users[user_id]
        write_to_log(f"Usuario eliminado: {user_id}")

# Crear la interfaz grafica
class UserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Usuarios con Bitacora")
        self.user_service = UserService()

        # Frame para formulario
        self.form_frame = tk.Frame(root, padx=10, pady=10)
        self.form_frame.pack(fill=tk.X)

        tk.Label(self.form_frame, text="ID Usuario:").grid(row=0, column=0)
        tk.Label(self.form_frame, text="Nombre:").grid(row=1, column=0)
        tk.Label(self.form_frame, text="Correo:").grid(row=2, column=0)

        self.id_entry = tk.Entry(self.form_frame)
        self.name_entry = tk.Entry(self.form_frame)
        self.email_entry = tk.Entry(self.form_frame)

        self.id_entry.grid(row=0, column=1)
        self.name_entry.grid(row=1, column=1)
        self.email_entry.grid(row=2, column=1)

        tk.Button(self.form_frame, text="Agregar Usuario", command=self.add_user).grid(row=3, column=0, pady=10)
        tk.Button(self.form_frame, text="Eliminar Usuario", command=self.delete_user).grid(row=3, column=1, pady=10)

        # Frame para mostrar usuarios
        self.list_frame = tk.Frame(root, padx=10, pady=10)
        self.list_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.list_frame, text="Usuarios Registrados:").pack(anchor="w")
        self.user_listbox = tk.Listbox(self.list_frame, height=10)
        self.user_listbox.pack(fill=tk.BOTH, expand=True)

        # Frame para bitacora
        self.log_frame = tk.Frame(root, padx=10, pady=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.log_frame, text="Bitacora:").pack(anchor="w")
        self.log_text = tk.Text(self.log_frame, height=10, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.log_frame, text="Actualizar Bitacora", command=self.update_log).pack(pady=5)
    def add_user(self):
        user_id = self.id_entry.get()
        name = self.name_entry.get()
        email = self.email_entry.get()

        if not user_id or not name or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            user_id = int(user_id)  # Validar que el ID sea un número
            self.user_service.create_user(user_id, {"name": name, "email": email})  # Cambiar aquí
            self.user_listbox.insert(tk.END, f"{user_id}: {name} - {email}")
            messagebox.showinfo("Éxito", f"Usuario {name} agregado.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self):
        selected = self.user_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un usuario para eliminar.")
            return

        user_info = self.user_listbox.get(selected[0])
        user_id = int(user_info.split(":")[0])

        try:
            self.user_service.delete_user(user_id)
            self.user_listbox.delete(selected[0])
            messagebox.showinfo("exito", f"Usuario con ID {user_id} eliminado.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        try:
            with open("bitacora.txt", "r") as log_file:
                self.log_text.insert(tk.END, log_file.read())
        except FileNotFoundError:
            self.log_text.insert(tk.END, "No hay registros en la bitacora.")
        self.log_text.config(state="disabled")

# Iniciar la aplicacion
if __name__ == "__main__":
    root = tk.Tk()
    app = UserApp(root)
    root.mainloop()
