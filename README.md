# pdf-encryptor
PDF Encryptor is a lightweight desktop application built with Python that allows you to encrypt multiple PDF files in bulk, each with a different password.

---

##  Quick Demo
1. Preparing the file names and passwords in an Excel file:
<img width="743" height="501" alt="Screenshot 2025-08-16 142559" src="https://github.com/user-attachments/assets/9873aeef-0769-442b-b3fe-713f37d0eb80" />


2. Starting the process, selecting the Excel file:
<img width="946" height="536" alt="Screenshot 2025-08-16 144321" src="https://github.com/user-attachments/assets/e2bf09d6-dac4-4884-86e7-b77ab37881c5" />


3. Select PDFs to encrypt:
<img width="949" height="536" alt="Screenshot 2025-08-16 141751" src="https://github.com/user-attachments/assets/1b0f007d-d7b3-420e-8491-7f017aeadf79" />


4. Select output folder:
<img width="949" height="534" alt="Screenshot 2025-08-16 143804" src="https://github.com/user-attachments/assets/d0ea1a4b-dd01-40d8-a263-f062d29bbcd7" />


5. Confirmation windows:
<img width="902" height="532" alt="Screenshot 2025-08-16 142651" src="https://github.com/user-attachments/assets/edd4e0f7-1829-497b-b2d4-5a49a9a39a63" />


6. Encryption complete windows:
<img width="360" height="251" alt="Screenshot 2025-08-16 142709" src="https://github.com/user-attachments/assets/6aecbd66-4deb-4eaf-afe5-cd1846b1899d" />


7. Output files:
<img width="242" height="142" alt="Screenshot 2025-08-16 143954" src="https://github.com/user-attachments/assets/75596091-86f7-48a4-987e-cc5dabd2fbaa" />


8. Process log (contains file names and their password):
<img width="387" height="222" alt="Screenshot 2025-08-16 144006" src="https://github.com/user-attachments/assets/da942a7c-6cc0-42b2-a4f6-f80de9c4dc8e" />

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
3. Prepare the Excel file containing file names and passwords
4. Extract and run `PDF Encrypt v1.0.0.exe`.  
5. Follow the steps:
   - Select your Excel file with `filename` and `password` columns  
   - Select the PDF files to encrypt  
   - Choose an output folder  
   - Review confirmation and click **Proceed**  
6. The output folder will contain:
   - Encrypted PDFs named `originalname_encrypted.pdf`  
   - A `password_list.txt` log with filenames and passwords

### B. Run from Source (Python)

```bash
git clone https://github.com/wendyanjasmara13/pdf-encryptor.git
cd pdf-encryptor
pip install -r requirements.txt
python src/pdf_encryptor.py
