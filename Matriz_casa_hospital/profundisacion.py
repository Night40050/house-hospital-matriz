import random
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os


class Coordinate:
    """Clase para manejar coordenadas en la matriz"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance_to(self, other):
        """Calcula la distancia Manhattan a otro punto"""
        return abs(self.x - other.x) + abs(self.y - other.y)

class HospitalDistribution:
    """Clase principal para el algoritmo de distribución de hospitales"""
    def __init__(self, rows, cols, num_hospitals, num_houses):
        self.rows = rows
        self.cols = cols
        self.num_hospitals = num_hospitals
        self.num_houses = num_houses
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.hospitals = set()
        self.houses = set()
        
        # Constantes
        self.MIN_HOSPITAL_DISTANCE = 3
        self.MAX_HOUSE_HOSPITAL_DISTANCE = 5
        
    def initialize_random_positions(self):
        """Inicializa posiciones aleatorias para hospitales y casas"""
        # Colocar hospitales
        while len(self.hospitals) < self.num_hospitals:
            x = random.randint(0, self.rows-1)
            y = random.randint(0, self.cols-1)
            new_pos = Coordinate(x, y)
            
            if self._is_valid_hospital_position(new_pos):
                self.hospitals.add(new_pos)
                self.grid[x][y] = 2  # 2 representa hospital
        
        # Colocar casas
        while len(self.houses) < self.num_houses:
            x = random.randint(0, self.rows-1)
            y = random.randint(0, self.cols-1)
            new_pos = Coordinate(x, y)
            
            if self.grid[x][y] == 0:  # Si la posición está vacía
                self.houses.add(new_pos)
                self.grid[x][y] = 1  # 1 representa casa

    def _is_valid_hospital_position(self, pos):
        """Verifica si una posición es válida para un nuevo hospital"""
        if self.grid[pos.x][pos.y] != 0:
            return False
            
        # Verificar distancia mínima con otros hospitales
        for hospital in self.hospitals:
            if pos.distance_to(hospital) < self.MIN_HOSPITAL_DISTANCE:
                return False
        return True
    
    def optimize_distribution(self):
        """Optimiza la distribución de hospitales usando búsqueda local"""
        best_score = self._calculate_score()
        improved = True
        
        while improved:
            improved = False
            for hospital in list(self.hospitals):
                old_pos = hospital
                best_new_pos = None
                
                # Buscar mejores posiciones en el vecindario
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        new_x = old_pos.x + dx
                        new_y = old_pos.y + dy
                        
                        if (0 <= new_x < self.rows and 
                            0 <= new_y < self.cols):
                            new_pos = Coordinate(new_x, new_y)
                            
                            # Simular movimiento
                            self.hospitals.remove(old_pos)
                            self.grid[old_pos.x][old_pos.y] = 0
                            
                            if self._is_valid_hospital_position(new_pos):
                                self.hospitals.add(new_pos)
                                self.grid[new_pos.x][new_pos.y] = 2
                                
                                new_score = self._calculate_score()
                                if new_score < best_score:
                                    best_score = new_score
                                    best_new_pos = new_pos
                                    improved = True
                                
                                # Revertir simulación
                                self.hospitals.remove(new_pos)
                                self.grid[new_pos.x][new_pos.y] = 0
                            
                            self.hospitals.add(old_pos)
                            self.grid[old_pos.x][old_pos.y] = 2
                
                if best_new_pos:
                    # Realizar el mejor movimiento encontrado
                    self.hospitals.remove(old_pos)
                    self.grid[old_pos.x][old_pos.y] = 0
                    self.hospitals.add(best_new_pos)
                    self.grid[best_new_pos.x][best_new_pos.y] = 2
    
    def _calculate_score(self):
        """Calcula el score de la distribución actual"""
        total_distance = 0
        for house in self.houses:
            min_distance = float('inf')
            for hospital in self.hospitals:
                distance = house.distance_to(hospital)
                min_distance = min(min_distance, distance)
            total_distance += min_distance
        return total_distance

class GUI:
    """Clase para la interfaz gráfica"""
    def __init__(self, master):
        self.master = master
        master.title("Distribución de Hospitales")
        
        # Obtener el directorio actual donde está el script
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Frame de configuración
        self.config_frame = ttk.Frame(master)
        self.config_frame.pack(pady=10)
        
        # Inicializar imágenes como None
        self.house_image = None
        self.hospital_image = None
        
        # Cargar imágenes
        self.load_images()
        
        # Inputs
        ttk.Label(self.config_frame, text="Filas:").grid(row=0, column=0)
        self.rows_var = tk.StringVar(value="10")
        ttk.Entry(self.config_frame, textvariable=self.rows_var).grid(row=0, column=1)
        
        ttk.Label(self.config_frame, text="Columnas:").grid(row=0, column=2)
        self.cols_var = tk.StringVar(value="10")
        ttk.Entry(self.config_frame, textvariable=self.cols_var).grid(row=0, column=3)
        
        ttk.Label(self.config_frame, text="Hospitales:").grid(row=1, column=0)
        self.hospitals_var = tk.StringVar(value="3")
        ttk.Entry(self.config_frame, textvariable=self.hospitals_var).grid(row=1, column=1)
        
        ttk.Label(self.config_frame, text="Casas:").grid(row=1, column=2)
        self.houses_var = tk.StringVar(value="10")
        ttk.Entry(self.config_frame, textvariable=self.houses_var).grid(row=1, column=3)
        
        # Botón de inicio
        ttk.Button(self.config_frame, text="Iniciar", command=self.start_simulation).grid(row=2, column=0, columnspan=4)
        
        # Canvas para la matriz
        self.canvas = tk.Canvas(master, width=500, height=500, bg='white')
        self.canvas.pack(pady=10)

    def load_images(self):
        """Carga y redimensiona las imágenes necesarias"""
        try:
            # Definir rutas de las imágenes
            house_path = os.path.join(self.current_dir, 'images', 'house.png')
            hospital_path = os.path.join(self.current_dir, 'images', 'hospital.png')
            
            # Asegurar que la carpeta images exista
            if not os.path.exists(os.path.join(self.current_dir, 'images')):
                os.makedirs(os.path.join(self.current_dir, 'images'))
                print("Carpeta 'images' creada. Coloca las imágenes allí.")
                return
            
            # Cargar icono de casa
            if os.path.exists(house_path):
                house_image = Image.open(house_path)
                self.house_image = ImageTk.PhotoImage(house_image.resize((40, 40)))
            else:
                print(f"No se encontró la imagen: {house_path}. Usando respaldo.")
                
            # Cargar icono de hospital
            if os.path.exists(hospital_path):
                hospital_image = Image.open(hospital_path)
                self.hospital_image = ImageTk.PhotoImage(hospital_image.resize((40, 40)))
            else:
                print(f"No se encontró la imagen: {hospital_path}. Usando respaldo.")

        except Exception as e:
            print(f"Error cargando imágenes: {str(e)}")
            self.house_image = None
            self.hospital_image = None

    def start_simulation(self):
        """Inicia la simulación con los parámetros ingresados"""
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            num_hospitals = int(self.hospitals_var.get())
            num_houses = int(self.houses_var.get())
            
            if num_hospitals <= 0 or num_houses <= 0:
                messagebox.showerror("Error", "Números deben ser mayores a 0")
                return
            
            self.distribution = HospitalDistribution(rows, cols, num_hospitals, num_houses)
            self.distribution.initialize_random_positions()
            self.draw_grid()
            
            # Optimizar y actualizar visualización
            self.master.after(100, self.optimize_step)
        except ValueError as e:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos")
    
    def optimize_step(self):
        """Ejecuta un paso de optimización y actualiza la visualización"""
        self.distribution.optimize_distribution()
        self.draw_grid()
    
    def draw_grid(self):
        """Dibuja la matriz en el canvas"""
        self.canvas.delete("all")
        
        cell_width = 500 // self.distribution.cols
        cell_height = 500 // self.distribution.rows
        
        # Asegurar tamaño mínimo de celdas
        cell_width = max(1, cell_width)
        cell_height = max(1, cell_height)
        
        # Dibujar cuadrícula
        for i in range(self.distribution.rows + 1):
            y = i * cell_height
            self.canvas.create_line(0, y, 500, y, fill="gray")
        for j in range(self.distribution.cols + 1):
            x = j * cell_width
            self.canvas.create_line(x, 0, x, 500, fill="gray")
        
        # Dibujar casas y hospitales
        for i in range(self.distribution.rows):
            for j in range(self.distribution.cols):
                x_center = j * cell_width + cell_width//2
                y_center = i * cell_height + cell_height//2
                
                if self.distribution.grid[i][j] == 1:  # Casa
                    if self.house_image:
                        self.canvas.create_image(x_center, y_center, image=self.house_image, anchor="center")
                    else:
                        self.canvas.create_rectangle(
                            x_center - 15, y_center - 15,
                            x_center + 15, y_center + 15,
                            fill="green", outline="")
                        
                elif self.distribution.grid[i][j] == 2:  # Hospital
                    if self.hospital_image:
                        self.canvas.create_image(x_center, y_center, image=self.hospital_image, anchor="center")
                    else:
                        self.canvas.create_oval(
                            x_center - 15, y_center - 15,
                            x_center + 15, y_center + 15,
                            fill="red", outline="")

def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()