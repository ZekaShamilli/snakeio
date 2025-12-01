import math
import matplotlib.pyplot as plt

# Yardımcı Fonksiyon: İki doğru parçasının kesişip kesişmediğini kontrol etmek için
# bir doğru parçasının bir noktayı içerip içermediğini kontrol eder
def on_segment(p, q, r):
    return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
            q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

def read_polygon(filename):
    """
    Belirtilen dosyadan poligonun köşe koordinatlarını okur.
    Her köşe (x, y) tuple'ı olarak temsil edilir.
    """
    polygon = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                        polygon.append((x, y))
                    except ValueError:
                        # Sayısal olmayan verileri yoksay
                        continue
    except FileNotFoundError:
        print(f"Hata: Dosya '{filename}' bulunamadı.")
        return []
    return polygon

def ccw(p, q, r):
    """
    Üç nokta p, q ve r'nin saat yönünün tersi (counter-clockwise - ccw) yönelimini bulur.
    > 0: Saat Yönünün Tersine (1)
    < 0: Saat Yönüne (2)
    = 0: Doğrusal (0)
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    return 1 if val > 0 else 2 if val < 0 else 0

def intersect(A, B, C, D):  # does edge <A,B> intersect edge <C,D>
    """
    <A, B> ve <C, D> doğru parçalarının kesişip kesişmediğini kontrol eder.
    """
    o1 = ccw(A, C, D)
    o2 = ccw(B, C, D)
    o3 = ccw(A, B, C)
    o4 = ccw(A, B, D)

    # Genel Durum
    if o1 != o2 and o3 != o4:
        return True

    # Özel Durumlar (Doğrusallık)
    # A, C-D üzerindeyse
    if o1 == 0 and on_segment(C, A, D): return True
    # B, C-D üzerindeyse
    if o2 == 0 and on_segment(C, B, D): return True
    # C, A-B üzerindeyse
    if o3 == 0 and on_segment(A, C, B): return True
    # D, A-B üzerindeyse
    if o4 == 0 and on_segment(A, D, B): return True

    return False

def is_visible(p1, p2, polygon):
    """
    <p1, p2> doğru parçasının poligonun hiçbir kenarını (kendisi hariç) kesip kesmediğini kontrol eder.
    İki köşe arasındaki görüş hattının poligonun içinde kalmasını sağlar.
    """
    n = len(polygon)
    p1_index = polygon.index(p1)
    p2_index = polygon.index(p2)
    if (p1_index + 1) % n == p2_index or (p2_index + 1) % n == p1_index:
        return True

    for i in range(n):
        edge_start = polygon[i]
        edge_end = polygon[(i + 1) % n]

       
        if intersect(p1, p2, edge_start, edge_end):
           
            if not (p1 in [edge_start, edge_end] or p2 in [edge_start, edge_end]):
                 return False

   
    return True


def compute_visibility(polygon):
    """
    Her v_i köşesinden hangi diğer köşelerin (v_j) görünür olduğunu hesaplar.
    Sonuç, anahtar olarak köşe (tuple) ve değer olarak görünür köşelerin listesi (list of tuples) olan
    bir sözlüktür.
    """
    n = len(polygon)
    visibility = {}
    
   
    vertex_map = {v: i for i, v in enumerate(polygon)}
    
    for i in range(n):
        p1 = polygon[i]
        visible_from_p1 = []
        for j in range(n):
            if i == j:
                continue
                
            p2 = polygon[j]
            
         
            is_visible_line = True
            for k in range(n):
                edge_start = polygon[k]
                edge_end = polygon[(k + 1) % n]
                
             
                if (k != i and k != (i - 1 + n) % n) and \
                   ((k + 1) % n != i and (k + 1) % n != (i - 1 + n) % n) and \
                   (k != j and k != (j - 1 + n) % n) and \
                   ((k + 1) % n != j and (k + 1) % n != (j - 1 + n) % n):
                    
                    if intersect(p1, p2, edge_start, edge_end):
                        is_visible_line = False
                        break
            
   
            if is_visible_line:

                 if is_visible(p1, p2, polygon):

                    visible_from_p1.append(vertex_map[p2])

        visibility[i] = visible_from_p1

    return visibility


def greedy_guard_placement(visibility, n): 
    """
    Poligonun tüm köşelerini gözetlemek için açgözlü (greedy) bir algoritma kullanarak
    minimum sayıda gözcü yerleştirir.
    """
    covered = set()
    guards = []
    
   
    while len(covered) < n:
      
        best_guard_index = -1
        max_uncovered = -1
        
        
        for guard_index, visible_vertices in visibility.items():
       
            uncovered_count = len(set(visible_vertices) - covered)
            
            if uncovered_count > max_uncovered:
                max_uncovered = uncovered_count
                best_guard_index = guard_index
        
 
        guards.append(best_guard_index)
        covered.update(visibility[best_guard_index])
        
    return guards

if __name__ == "__main__":

    test_polygon_coords = [
        (0, 0),
        (6, 0),
        (6, 4),
        (3, 2), 
        (0, 4)
    ]
    

    print("--- Sanat Galerisi Gözcü Yerleştirme ---")
    
    polygon = test_polygon_coords
    
    if not polygon:

        print("Poligon verisi bulunamadı veya okunamadı.")
    else:

        visibility = compute_visibility(polygon)
        

            
        guards = greedy_guard_placement(visibility, len(polygon))

        guard_coords = [polygon[i] for i in guards]
        
        print(f"Poligon Köşe Sayısı (n): {len(polygon)}")
        print(f"Gözcü yerleştirilen köşe indisleri: {guards}")
        print(f"Gözcüler (koordinatlar): {guard_coords}")
        
       
        min_guards_needed = math.floor(len(polygon) / 3)
        print(f"Teorik minimum gözcü sayısı (floor(n/3)): {min_guards_needed}")

       
        x = [p[0] for p in polygon]
        y = [p[1] for p in polygon]
        
      
        x.append(x[0])
        y.append(y[0])
        
        plt.figure(figsize=(8, 6))
        
      
        plt.plot(x, y, 'b-', label='Poligon Sınırı')
        
       
        for i, (px, py) in enumerate(polygon):
            plt.plot(px, py, 'bo')
            plt.text(px, py + 0.1, f'v{i}', ha='center')
            
   
        guard_x = [p[0] for p in guard_coords]
        guard_y = [p[1] for p in guard_coords]
        plt.plot(guard_x, guard_y, 'r*', markersize=15, label='Gözcüler')
        
        plt.title(f'Gözcü Yerleşimi (Greedy Algoritma)')
        plt.xlabel('X Koordinatı')
        plt.ylabel('Y Koordinatı')
        plt.legend()
        plt.grid(True)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()