import numpy as np

class SAWEngine:
    @staticmethod
    def calculate_saw(matrix, weights, types):
        """
        matrix: 2D list berisi angka (Alternatif x Kriteria)
        weights: List bobot (misal: [0.5, 0.5])
        types: List tipe ('benefit' atau 'cost')
        """
        try:
            data = np.array(matrix, dtype=float)
            w = np.array(weights, dtype=float)
            baris, kolom = data.shape
            norm_matrix = np.zeros((baris, kolom))

            # Proses Normalisasi
            for j in range(kolom):
                column = data[:, j]
                if types[j].lower() == 'benefit':
                    max_val = np.max(column)
                    norm_matrix[:, j] = column / max_val if max_val != 0 else 0
                else:
                    min_val = np.min(column)
                    norm_matrix[:, j] = np.where(column != 0, min_val / column, 0)
            
            # Perankingan (V)
            final_scores = np.dot(norm_matrix, w)
            return final_scores.tolist()
        except Exception as e:
            return f"Error: {str(e)}"