import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time

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
        
        # Frame de configuración
        self.config_frame = ttk.Frame(master)
        self.config_frame.pack(pady=10)
        
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
        self.canvas = tk.Canvas(master, width=500, height=500)
        self.canvas.pack(pady=10)
        
    def start_simulation(self):
        """Inicia la simulación con los parámetros ingresados"""
        rows = int(self.rows_var.get())
        cols = int(self.cols_var.get())
        num_hospitals = int(self.hospitals_var.get())
        num_houses = int(self.houses_var.get())
        
        self.distribution = HospitalDistribution(rows, cols, num_hospitals, num_houses)
        self.distribution.initialize_random_positions()
        self.draw_grid()
        
        # Optimizar y actualizar visualización
        self.master.after(100, self.optimize_step)
    
    def optimize_step(self):
        """Ejecuta un paso de optimización y actualiza la visualización"""
        self.distribution.optimize_distribution()
        self.draw_grid()
        
    def draw_grid(self):
        """Dibuja la matriz en el canvas"""
        self.canvas.delete("all")
        cell_width = 500 // self.distribution.cols
        cell_height = 500 // self.distribution.rows
        
        for i in range(self.distribution.rows):
            for j in range(self.distribution.cols):
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                
                # Dibujar celda
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray")
                
                # Dibujar contenido
                if self.distribution.grid[i][j] == 1:  # Casa
                    self.canvas.create_rectangle(x1+5, y1+5, x2-5, y2-5, fill="green")
                elif self.distribution.grid[i][j] == 2:  # Hospital
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="red")

def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()