import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import pikepdf


# ---------- Helpers ----------

def truncate_ellipsis(text: str, width: int) -> str:
    """Truncate to 'width' and add … if needed; pad with spaces to stay fixed-width."""
    s = "" if text is None else str(text)
    if len(s) > width:
        return s[:max(0, width - 1)] + "…"
    return s.ljust(width)


def build_preview_table(rows):
    """
    rows: list of tuples (index, filename, password)
    Returns a nicely formatted fixed-width ASCII table (single-line per row).
    """
    # Fixed column widths
    w_no, w_file, w_pwd = 4, 52, 28

    def sep():
        return "+" + "-"*(w_no+2) + "+" + "-"*(w_file+2) + "+" + "-"*(w_pwd+2) + "+\n"

    header  = sep()
    header += "| " + truncate_ellipsis("No", w_no)   + " | "
    header += truncate_ellipsis("File Name", w_file) + " | "
    header += truncate_ellipsis("Password", w_pwd)   + " |\n"
    header += sep()

    body = ""
    for i, fname, pwd in rows:
        body += "| " + truncate_ellipsis(str(i), w_no)   + " | "
        body += truncate_ellipsis(fname, w_file)         + " | "
        body += truncate_ellipsis(pwd, w_pwd)            + " |\n"

    return header + body + sep()


def encrypt_pdf(input_pdf: str, output_pdf: str, password: str) -> tuple[bool, str | None]:
    """Encrypt one PDF. Returns (success, error_message). AES-256 by default (pikepdf)."""
    try:
        with pikepdf.open(input_pdf) as pdf:
            pdf.save(
                output_pdf,
                encryption=pikepdf.Encryption(
                    user=str(password),
                    owner=str(password)
                )
            )
        return True, None
    except Exception as e:
        return False, str(e)


# ---------- Main workflow ----------

def main():
    root = tk.Tk()
    root.withdraw()  # we won't show a main window

    # Step 1: Select Excel
    excel_path = filedialog.askopenfilename(
        title="Select Excel file containing passwords (columns: filename, password)",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not excel_path:
        messagebox.showinfo("Cancelled", "No Excel file selected.")
        return

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read Excel file:\n{e}")
        return

    df.columns = [str(c).strip().lower() for c in df.columns]
    if "filename" not in df.columns or "password" not in df.columns:
        messagebox.showerror("Error", "Excel must contain 'filename' and 'password' columns.")
        return

    # Step 2: Select PDFs
    pdf_paths = filedialog.askopenfilenames(
        title="Select PDF files to encrypt",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not pdf_paths:
        messagebox.showinfo("Cancelled", "No PDF files selected.")
        return

    # Step 3: Select output folder
    output_folder = filedialog.askdirectory(title="Select output folder")
    if not output_folder:
        messagebox.showinfo("Cancelled", "No output folder selected.")
        return

    # Build preview data
    preview_rows = []
    pairs = []  # (pdf_path, password or "(NOT FOUND)")
    for idx, pdf_path in enumerate(pdf_paths, start=1):
        fname = os.path.basename(pdf_path)
        row = df[df["filename"] == fname]
        if not row.empty:
            pwd = str(row["password"].values[0])
        else:
            pwd = "(NOT FOUND)"
        preview_rows.append((idx, fname, pwd))
        pairs.append((pdf_path, pwd))

    # Confirmation window
    confirm = {
        "proceed": False,
        "overwrite": tk.BooleanVar(value=False),
        "add_suffix": tk.BooleanVar(value=True),  # NEW: control "_encrypted" suffix
    }

    top = tk.Toplevel(root)
    top.title("Confirm Encryption List")
    top.geometry("900x600")

    header_text = (
        f"Output folder: {output_folder}\n"
        f"Excel: {os.path.basename(excel_path)}\n"
        f"Total selected PDF: {len(pdf_paths)}\n\n"
    )
    table_text = build_preview_table(preview_rows)

    # Frame with Text + scrollbars
    frame = tk.Frame(top)
    frame.pack(expand=True, fill="both", padx=8, pady=8)

    text = tk.Text(frame, wrap="none", font=("Consolas", 10))
    yscroll = tk.Scrollbar(frame, orient="vertical", command=text.yview)
    xscroll = tk.Scrollbar(frame, orient="horizontal", command=text.xview)
    text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

    text.insert("end", header_text + table_text)
    text.configure(state="disabled")

    text.pack(side="left", expand=True, fill="both")
    yscroll.pack(side="right", fill="y")
    xscroll.pack(side="bottom", fill="x")

    # Options row
    options_frame = tk.Frame(top)
    options_frame.pack(pady=(4, 0))

    overwrite_chk = tk.Checkbutton(
        options_frame,
        text="Replace original files (instead of saving to the output folder with a new name)",
        variable=confirm["overwrite"]
    )
    overwrite_chk.grid(row=0, column=0, sticky="w", padx=4, pady=2)

    suffix_chk = tk.Checkbutton(
        options_frame,
        text='Add "_encrypted" to filename (applies only when not replacing originals)',
        variable=confirm["add_suffix"]
    )
    suffix_chk.grid(row=1, column=0, sticky="w", padx=4, pady=2)

    # Buttons
    btn_frame = tk.Frame(top)
    btn_frame.pack(pady=8)
    def on_proceed():
        confirm["proceed"] = True
        top.destroy()
    def on_cancel():
        top.destroy()
    tk.Button(btn_frame, text="Proceed", width=12, command=on_proceed).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Cancel",  width=12, command=on_cancel).pack(side="left", padx=6)

    top.protocol("WM_DELETE_WINDOW", on_cancel)
    top.grab_set()
    root.wait_window(top)

    if not confirm["proceed"]:
        messagebox.showinfo("Cancelled", "Operation cancelled.")
        return

    # Step 4: Encrypt with progress bar
    progress_win = tk.Toplevel(root)
    progress_win.title("Encrypting PDFs")
    tk.Label(progress_win, text="Encrypting files, please wait...").pack(pady=10)
    progress = ttk.Progressbar(progress_win, orient="horizontal", length=420, mode="determinate")
    progress.pack(padx=20, pady=10)
    progress["maximum"] = len(pairs)
    progress_win.update_idletasks()

    log_lines = []
    success_count = 0
    skipped_count = 0
    error_count = 0

    for i, (pdf_path, pwd) in enumerate(pairs, start=1):
        fname = os.path.basename(pdf_path)
        base, ext = os.path.splitext(fname)

        if confirm["overwrite"].get():
            # Replace original filename (in the chosen output folder)
            output_pdf = os.path.join(output_folder, fname)
        else:
            if confirm["add_suffix"].get():
                output_pdf = os.path.join(output_folder, f"{base}_encrypted{ext}")
            else:
                output_pdf = os.path.join(output_folder, f"{base}{ext}")

        if pwd == "(NOT FOUND)":
            log_lines.append(f"{fname}\t(NOT FOUND)")
            skipped_count += 1
        else:
            ok, err = encrypt_pdf(pdf_path, output_pdf, pwd)
            if ok:
                log_lines.append(f"{os.path.basename(output_pdf)}\t{pwd}")
                success_count += 1
            else:
                log_lines.append(f"{fname}\tERROR: {err}")
                error_count += 1

        progress["value"] = i
        progress_win.update_idletasks()

    progress_win.destroy()

    # Step 5: Write password list
    log_path = os.path.join(output_folder, "password_list.txt")
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("File Name\tPassword\n")
            f.write("\n".join(log_lines))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write password_list.txt:\n{e}")
        return

    # Final results + Donation window
    done = tk.Toplevel(root)
    done.title("Done")

    summary = (
        "Encryption complete!\n\n"
        f"Saved password list to:\n{log_path}\n\n"
        f"Summary:\n"
        f"- Encrypted: {success_count}\n"
        f"- Skipped (no password): {skipped_count}\n"
        f"- Errors: {error_count}\n"
    )
    tk.Label(done, text=summary, justify="left").pack(anchor="w", padx=12, pady=(12, 8))

    # Donation copy (EN + ID)
    donate_text_en = (
        "This tool is free to use. If you found it helpful and want to support the creator "
        "(so he can grab some coffee ☕ and help his parents ❤️), you can donate here:"
    )
    donate_text_id = (
        "Alat ini gratis tis tis. Kalau kamu merasa terbantu dan ingin traktir pembuatnya "
        "biar bisa jajan ☕ sekaligus bantu orang tua ❤️, silakan donasi di sini:"
    )

    # English copy first
    tk.Label(done, text=donate_text_en, wraplength=520, justify="left").pack(anchor="w", padx=12, pady=(4, 2))

    # PayPal button
    def open_paypal():
        webbrowser.open("https://paypal.me/wendyanjasmara", new=2)
    tk.Button(done, text="☕ Donate via PayPal", width=24, command=open_paypal).pack(anchor="w", padx=12, pady=2)

    # Indonesian copy after PayPal
    tk.Label(done, text=donate_text_id, wraplength=520, justify="left").pack(anchor="w", padx=12, pady=(8, 2))

    # Saweria button
    def open_saweria():
        webbrowser.open("https://saweria.co/siapahayoo13", new=2)
    tk.Button(done, text="🍵 Donasi via Saweria", width=24, command=open_saweria).pack(anchor="w", padx=12, pady=2)

    # Close button
    tk.Button(done, text="Close", width=12, command=done.destroy).pack(pady=(12, 12))

    done.grab_set()
    root.wait_window(done)


if __name__ == "__main__":
    main()
