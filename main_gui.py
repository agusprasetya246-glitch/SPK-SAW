import FreeSimpleGUI as sg
from saw_engine import SAWEngine

def create_window():
    layout = [
        [sg.Text("SPK Metode SAW Kelompok 3", font=("Arial", 14, "bold"))],
        [sg.Frame("Langkah 1: Konfigurasi & Bobot", [
            [sg.Text("Jumlah Kriteria:"), 
             sg.Input(key="-IN_K-", size=(5,1), enable_events=True), 
             sg.Button("Generate")]
        ])],
        [sg.Column([[]], key="-COL_K-", scrollable=True, vertical_scroll_only=True, size=(550, 120), visible=False)], 
        
        [sg.Frame("Langkah 2: Data Alternatif", [
            [sg.Text("Nama Alternatif:"), sg.Input(key="-ALT_NAME-", size=(15,1)), sg.Button("Tambah Baris")],
            [sg.HorizontalSeparator()],
            [sg.Column([[]], key="-TABLE_HEADER-")],
            # Penting: Column ini menjadi tempat baris-baris yang di-pin
            [sg.Column([[]], key="-TABLE_BODY-", scrollable=True, size=(580, 250), expand_x=True, expand_y=True)]
        ])],

        [sg.Button("Hitung Sekarang", button_color="green"), sg.Button("Reset")],
        [sg.Multiline(size=(70, 6), key="-OUT-", disabled=True)]
    ]
    return sg.Window("Sistem Pendukung Keputusan", layout, finalize=True)

def main():
    window = create_window()
    alt_count = 0 
    generated = False 

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: break

        # Filter Numerik
        if event == "-IN_K-" or (event and (event.startswith("-W") or "_VAL_" in event)):
            if values[event] and values[event][-1] not in ('0123456789.'):
                window[event].update(values[event][:-1])

        if event == "Generate":
            if generated: continue
            try:
                n = int(values["-IN_K-"])
                k_layout = []
                header_layout = [sg.Text("Nama Alternatif", size=(15,1), justification='center')]
                for i in range(n):
                    k_layout.append([
                        sg.Text(f"C{i+1} Nama:"), sg.Input(key=f"-NAME_K{i}-", size=(10,1)),
                        sg.Text("Bobot %:"), sg.Input(key=f"-W{i}-", size=(5,1), enable_events=True),
                        sg.Combo(['Benefit', 'Cost'], default_value='Benefit', key=f"-T{i}-", readonly=True)
                    ])
                    header_layout.append(sg.Text(f"C{i+1}", size=(7,1), justification='center'))
                
                window.extend_layout(window["-COL_K-"], k_layout)
                window["-COL_K-"].update(visible=True)
                window.extend_layout(window["-TABLE_HEADER-"], [header_layout])
                generated = True
            except: sg.popup_error("Masukkan angka!")

        if event == "Tambah Baris":
            if not generated: sg.popup_error("Generate kriteria dulu!"); continue
            try:
                n = int(values["-IN_K-"])
                name = values["-ALT_NAME-"] or f"Alt {alt_count + 1}"
                
                # Menggunakan sg.pin agar layout merapat saat di-hide
                row_content = [
                    sg.Input(name, key=f"-ALT_NAME_{alt_count}-", size=(17,1)),
                    *[sg.Input("", key=f"-VAL_{alt_count}_{j}-", size=(8,1), enable_events=True) for j in range(n)],
                    sg.Button("X", key=f"-DEL_{alt_count}-", button_color=("white", "red"), size=(2,1))
                ]
                
                row_pinned = [sg.pin(sg.Column([row_content], key=f"-ROW_{alt_count}-"))]
                
                window.extend_layout(window["-TABLE_BODY-"], [row_pinned])
                window["-ALT_NAME-"].update("")
                window["-TABLE_BODY-"].contents_changed()
                alt_count += 1
            except: pass

        if event and event.startswith("-DEL_"):
            idx = event.split("_")[1].replace("-", "")
            window[f"-ROW_{idx}-"].update(visible=False)
            window[f"-ALT_NAME_{idx}-"].update("DELETED_ITEM")

        if event == "Hitung Sekarang":
            try:
                n = int(values["-IN_K-"])
                raw_weights = [float(values[f"-W{i}-"]) for i in range(n)]
                if sum(raw_weights) != 100:
                    sg.popup_error(f"Total harus harus 100%! (Sekarang: {sum(raw_weights)}%)"); continue
                
                weights = [w/100 for w in raw_weights]
                types = [values[f"-T{i}-"] for i in range(n)]
                
                matrix, final_names = [], []
                for i in range(alt_count):
                    if values[f"-ALT_NAME_{i}-"] == "DELETED_ITEM": continue
                    final_names.append(values[f"-ALT_NAME_{i}-"])
                    matrix.append([float(values[f"-VAL_{i}_{j}-"]) if values[f"-VAL_{i}_{j}-"] else 0.0 for j in range(n)])
                
                if not matrix: sg.popup_error("Data kosong!"); continue
                
                scores = SAWEngine.calculate_saw(matrix, weights, types)
                ranked = sorted(zip(final_names, scores), key=lambda x: x[1], reverse=True)
                
                res = "HASIL PERANKINGAN:\n" + "="*40 + "\n"
                for idx, (nm, sc) in enumerate(ranked):
                    res += f"Peringkat {idx+1}: {nm} \t Skor: {sc:.4f}\n"
                window["-OUT-"].update(res)
            except Exception as e: sg.popup_error(f"Error: {e}")

        if event == "Reset":
            window.close()
            main()
            break

    window.close()

if __name__ == "__main__": main()