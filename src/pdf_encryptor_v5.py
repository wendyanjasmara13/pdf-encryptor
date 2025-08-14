import os
import tkinter as tk
from tkinter import filedialog, messagebox
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
    # Fixed column widths (tweak as you like)
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
                    # No 'R' param => pikepdf uses strongest available (AES-256)
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

    # Read Excel and validate columns
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

    # Show confirmation window (Toplevel) with scrollbars, monospace table
    confirm = {"proceed": False}

    top = tk.Toplevel(root)
    top.title("Confirm Encryption List")
    top.geometry("900x500")  # wider by default

    # Header info
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

    # Buttons
    btn_frame = tk.Frame(top)
    btn_frame.pack(pady=6)
    def on_proceed():
        confirm["proceed"] = True
        top.destroy()
    def on_cancel():
        top.destroy()
    tk.Button(btn_frame, text="Proceed", width=12, command=on_proceed).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Cancel",  width=12, command=on_cancel).pack(side="left", padx=6)

    # Make closing the window equal to cancel
    top.protocol("WM_DELETE_WINDOW", on_cancel)

    # Wait until window is closed (no second Tk mainloop)
    top.grab_set()
    root.wait_window(top)

    if not confirm["proceed"]:
        messagebox.showinfo("Cancelled", "Operation cancelled.")
        return

    # Step 4: Encrypt
    log_lines = []
    success_count = 0
    skipped_count = 0
    error_count = 0

    for pdf_path, pwd in pairs:
        fname = os.path.basename(pdf_path)
        base, ext = os.path.splitext(fname)
        output_pdf = os.path.join(output_folder, f"{base}_encrypted{ext}")

        if pwd == "(NOT FOUND)":
            log_lines.append(f"{fname}\t(NOT FOUND)")
            skipped_count += 1
            continue

        ok, err = encrypt_pdf(pdf_path, output_pdf, pwd)
        if ok:
            log_lines.append(f"{os.path.basename(output_pdf)}\t{pwd}")
            success_count += 1
        else:
            log_lines.append(f"{fname}\tERROR: {err}")
            error_count += 1

    # Step 5: Write password list
    log_path = os.path.join(output_folder, "password_list.txt")
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("File Name\tPassword\n")
            f.write("\n".join(log_lines))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write password_list.txt:\n{e}")
        return

    messagebox.showinfo(
        "Done",
        "Encryption complete!\n\n"
        f"Saved password list to:\n{log_path}\n\n"
        f"Summary:\n"
        f"- Encrypted: {success_count}\n"
        f"- Skipped (no password): {skipped_count}\n"
        f"- Errors: {error_count}"
    )

if __name__ == "__main__":
    main()
