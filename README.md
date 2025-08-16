# pdf-encryptor
PDF Encryptor is a lightweight desktop application built with Python that allows you to encrypt multiple PDF files in bulk, each with a different password.

---

##  Quick Demo

![PDF Encryptor Demo Screenshot](<img width="938" height="528" alt="Screenshot 2025-08-16 141246" src="https://github.com/user-attachments/assets/ffa73d29-6d79-4a8c-a1bb-e71de8aca1df" />)


*Replace `screenshots/screenshot.png` with your actual app screenshot.*

---

## Features

- **AES-256 Encryption** for strong security
- Works completely offline (no internet needed)
- Friendly GUI (no programming required)
- **Batch processing** — encrypt multiple PDFs in one go  
- Import passwords from an Excel file (`filename` + `password` columns)  
- Select a custom output folder  
- Encrypted files automatically receive `_encrypted` suffix  
- Confirmation screen previews files and passwords before encryption  
- Password log ensures easy verification and accountability

---

## License & Support

- License: MIT License — freely use, modify, and distribute (see LICENSE).
- Donations (optional, but appreciated): https://saweria.co/siapahayoo13

---

## ​ How to Use

### A. Download & Run (Windows executable)

1. Navigate to the [**Releases** page](https://github.com/wendyanjasmara13/pdf-encryptor/releases/latest).  
2. Download the `PDF.Encrypt.v1.0.0.7z`.  
3. Extract and run `PDF Encrypt v1.0.0exe`.  
4. Follow the steps:
   - Select your Excel file with `filename` and `password` columns  
   - Select the PDF files to encrypt  
   - Choose an output folder  
   - Review confirmation and click **Proceed**  
5. The output folder will contain:
   - Encrypted PDFs named `originalname_encrypted.pdf`  
   - A `password_list.txt` log with filenames and passwords

### B. Run from Source (Python)

```bash
git clone https://github.com/wendyanjasmara13/pdf-encryptor.git
cd pdf-encryptor
pip install -r requirements.txt
python src/pdf_encryptor.py
