import FreeSimpleGUI as sg
from saw_engine import SAWEngine

def create_window():
    layout = [
        [sg.Text("SPK Metode SAW (Modular Version)", font=("Arial", 14, "bold"))],
        [sg.Frame("Langkah 1: Konfigurasi", [
            [sg.Text("Jumlah Kriteria:"), sg.Input(key="-IN_K-", size=(5,1)), 
             sg.Button("Generate Input")]
        ])],
        [sg.Column([], key="-COL_K-")], 
        [sg.Frame("Langkah 2: Data Alternatif", [
            [sg.Text("Nama:"), sg.Input(key="-ALT_NAME-", size=(12,1)),
             sg.Text("Data (koma):"), sg.Input(key="-ALT_VAL-", size=(20,1)),
             sg.Button("Tambah")]
        ])],
        [sg.Table(values=[], headings=["Alternatif"], key="-TABLE-", 
                  auto_size_columns=True, num_rows=6, justification='center')],
        [sg.Button("Hitung Sekarang", button_color="green"), sg.Button("Reset")],
        [sg.Multiline(size=(60, 6), key="-OUT-", echo_stdout_stderr=True, disabled=True)]
    ]
    return sg.Window("Sistem Pendukung Keputusan", layout, finalize=True)

def main():
    window = create_window()
    alt_names = []
    alt_values = []

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        # Generate baris input untuk Bobot & Tipe secara dinamis
        if event == "Generate Input":
            try:
                n = int(values["-IN_K-"])
                k_layout = [[sg.Text(f"C{i+1} Bobot:"), sg.Input(key=f"-W{i}-", size=(5,1)),
                             sg.Combo(['Benefit', 'Cost'], default_value='Benefit', key=f"-T{i}-")] 
                            for i in range(n)]
                window.extend_layout(window["-COL_K-"], k_layout)
                window["-TABLE-"].update(headings=["Alternatif"] + [f"C{i+1}" for i in range(n)])
            except:
                sg.popup_error("Isi jumlah kriteria dengan angka!")

        # Menambahkan data ke list dan tabel
        if event == "Tambah":
            try:
                name = values["-ALT_NAME-"]
                raw_data = [float(x.strip()) for x in values["-ALT_VAL-"].split(",")]
                if len(raw_data) != int(values["-IN_K-"]):
                    sg.popup_error("Jumlah data harus sama dengan jumlah kriteria!")
                    continue
                
                alt_names.append(name)
                alt_values.append(raw_data)
                
                # Update tabel tampilan
                table_display = [[alt_names[i]] + alt_values[i] for i in range(len(alt_values))]
                window["-TABLE-"].update(values=table_display)
            except:
                sg.popup_error("Format salah! Contoh: 80, 90, 75")

        # Memanggil fungsi di file saw_engine.py
        if event == "Hitung Sekarang":
            try:
                n = int(values["-IN_K-"])
                weights = [float(values[f"-W{i}-"]) for i in range(n)]
                types = [values[f"-T{i}-"] for i in range(n)]
                
                # PROSES BACKEND
                scores = SAWEngine.calculate_saw(alt_values, weights, types)
                
                # Tampilkan hasil
                ranked = sorted(zip(alt_names, scores), key=lambda x: x[1], reverse=True)
                res_str = "HASIL PERANKINGAN:\n"
                for i, (name, score) in enumerate(ranked):
                    res_str += f"Peringkat {i+1}: {name} ({score:.4f})\n"
                window["-OUT-"].update(res_str)
            except Exception as e:
                sg.popup_error(f"Gagal menghitung: {e}")

        if event == "Reset":
            window.close()
            main()

    window.close()

if __name__ == "__main__":
    main()