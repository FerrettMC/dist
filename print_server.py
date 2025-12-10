from flask import Flask, request
from flask_cors import CORS
import win32print
import win32ui
import win32con


app = Flask(__name__)
CORS(app)  # allow all origins, including your website

# For testing without a printer, uncomment this section to write to a file instead
# @app.post("/print")
# def print_ticket():
#     text = request.json.get("text", "")
    
#     with open("TEST_OUTPUT.txt", "a") as f:
#         f.write(text)
#         f.write("\n")

#     return {"status": "ok"}





@app.post("/print")
def print_ticket():
    text = request.json.get("text", "NO TEXT RECEIVED")

    printer_name = win32print.GetDefaultPrinter()

    # Create a device context for the printer
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer_name)
    hDC.StartDoc("Deli Ticket")
    hDC.StartPage()

    # --- Create a huge font ---
    huge_font = win32ui.CreateFont({
        "name": "Arial",  # choose a font
        "height": 400,    # very large text
        "weight": 700,    # bold
    })
    hDC.SelectObject(huge_font)

    # --- Center the text on the page ---
    page_width = hDC.GetDeviceCaps(win32con.HORZRES)
    page_height = hDC.GetDeviceCaps(win32con.VERTRES)

    # If multiple lines, print each line centered vertically with spacing
    lines = text.splitlines()
    total_height = len(lines) * 400  # roughly line height = font height
    start_y = (page_height - total_height) // 2

    for i, line in enumerate(lines):
        line_width, line_height = hDC.GetTextExtent(line)
        x = (page_width - line_width) // 2
        y = start_y + i * 400
        hDC.TextOut(x, y, line)

    hDC.EndPage()
    hDC.EndDoc()
    hDC.DeleteDC()

    return {"status": "printed"}


app.run(host="127.0.0.1", port=5000)
