import FreeSimpleGUI as sg
from saw_engine import SAWEngine

def create_window():
    layout = [
        [sg.Text("SPK Metode SAW (Modular Version)", font=("Arial", 14, "bold"))],
        [sg.Frame("Langkah 1: Konfigurasi", [
            [sg.Text("Jumlah Kriteria:"), 
             sg.Input(key="-IN_K-", size=(5,1), enable_events=True), 
             sg.Button("Generate Input")]
        ])],
        # Perbaikan: Menambahkan container khusus untuk input dinamis
        [sg.Column([[]], key="-COL_K-", scrollable=True, vertical_scroll_only=True, size=(400, 150), visible=False)], 
        [sg.Frame("Langkah 2: Data Alternatif", [
            [sg.Text("Nama:"), sg.Input(key="-ALT_NAME-", size=(12,1)),
             sg.Text("Data (koma):"), sg.Input(key="-ALT_VAL-", size=(20,1)),
             sg.Button("Tambah")]
        ])],
        [sg.Table(values=[], headings=["Alternatif", "Data Kriteria (Array)"], key="-TABLE-", 
                  auto_size_columns=False, col_widths=[15, 40], num_rows=6, justification='center')],
        [sg.Button("Hitung Sekarang", button_color="green"), sg.Button("Reset")],
        [sg.Multiline(size=(60, 6), key="-OUT-", echo_stdout_stderr=True, disabled=True)]
    ]
    return sg.Window("Sistem Pendukung Keputusan", layout, finalize=True)

def main():
    window = create_window()
    alt_names = []
    alt_values = []
    generated = False

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "-IN_K-" or event.startswith("-W"):
            if values[event] and values[event][-1] not in ('0123456789'):
                window[event].update(values[event][:-1])

        if event == "Generate Input":
            if generated:
                sg.popup_error("Klik 'Reset' untuk mengubah jumlah kriteria!")
                continue

            try:
                n = int(values["-IN_K-"])
                if n <= 0: raise ValueError

                k_layout = []
                for i in range(n):
                    # Dibungkus dalam satu list baris
                    row = [sg.Text(f"Nama C{i+1}:"),
                           sg.Input(key=f"-NAME_K{i}-", size=(10,1)), # Tambahan input nama
                           sg.Text("Bobot (%):"),
                           sg.Input(key=f"-W{i}-", size=(5,1), enable_events=True),
                           sg.Combo(['Benefit', 'Cost'], default_value='Benefit', key=f"-T{i}-", readonly=True)]
                    k_layout.append(row)

                window.extend_layout(window["-COL_K-"], k_layout)
                window["-COL_K-"].update(visible=True)
                generated = True

            except Exception as e:
                sg.popup_error(f"Masukkan angka jumlah kriteria yang valid! Error: {e}")

        # Menambahkan data ke list dan tabel
        if event == "Tambah":
            try:
                name = values["-ALT_NAME-"]

                raw_data = [float(x.strip()) for x in values["-ALT_VAL-"].split(",")]
                n_kriteria = int(values["-IN_K-"])

                if len(raw_data) != n_kriteria:
                    sg.popup_error(f"Data harus berjumlah {n_kriteria} kriteria!")
                    continue
                
                alt_names.append(name)
                alt_values.append(raw_data)
                
                # Update tabel tampilan
                table_display = [[alt_names[i] + str(alt_values[i])] for i in range(len(alt_values))]
                window["-TABLE-"].update(values=table_display)

                window["-ALT_NAME-"].update("")
                window["-ALT_VAL-"].update("")
            except:
                sg.popup_error("Format data salah! Gunakan angka dipisah koma (contoh: 80, 90, 75)")

        # Memanggil fungsi di file saw_engine.py
        if event == "Hitung Sekarang":
            try:
                n = int(values["-IN_K-"])
                raw_weights = []

                for i in range(n):
                    w_val = values[f"-W{i}-"]
                    if not w_val:
                        sg.popup_error(f"Bobot kriteria {i+1} belum diisi!")
                        raise Exception("Incomplete weights")
                    raw_weights.append(float(w_val))

                total_w = sum(raw_weights)
                if total_w != 100:
                    sg.popup_error(f"Total bobot harus 100%! Sekarang: {total_w}%")
                    continue

                weights = [w / 100 for w in raw_weights]
                types = [values[f"-T{i}-"] for i in range(n)]

                k_names = [values[f"-NAME_K{i}-"] if values[f"-NAME_K{i}-"] else f"C{i+1}" for i in range(n)]
                
                # PROSES BACKEND
                scores = SAWEngine.calculate_saw(alt_values, weights, types)
                
                # Tampilkan hasil
                ranked = sorted(zip(alt_names, scores), key=lambda x: x[1], reverse=True)
                res_str = "HASIL PERANKINGAN:\n" + "-"*30 + "\n"
                for i, (name, score) in enumerate(ranked):
                    res_str += f"Peringkat {i+1}: {name} ({score:.4f})\n"
                window["-OUT-"].update(res_str)
            except Exception as e:
                if str(e) != "Incomplete weights":
                    sg.popup_error(f"Error: {e}")

        if event == "Reset":
            window.close()
            main()
            break

    window.close()

if __name__ == "__main__":
    main()