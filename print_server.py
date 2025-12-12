from flask import Flask, request
from waitress import serve
from flask_cors import CORS
import win32print
import win32ui
import win32con
import threading
printer_lock = threading.Lock()


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

@app.get("/printer-status")
def printer_status():
    try:
        printer_name = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(printer_name)
        win32print.ClosePrinter(hPrinter)
        return {"status": "online"}
    except:
        return {"status": "offline"}, 503


@app.post("/print")
def print_ticket():
    with printer_lock:
        try:
            text = request.json.get("text", "NO TEXT RECEIVED")

            # Validate input
            if not text.strip():
                return {"status": "error", "message": "Empty text received"}, 400

            printer_name = win32print.GetDefaultPrinter()
            if not printer_name:
                return {"status": "error", "message": "No default printer found"}, 500

            # Create a device context for the printer
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)

            try:
                hDC.StartDoc("Deli Ticket")
                hDC.StartPage()

            # --- Center the text on the page ---
                page_width = hDC.GetDeviceCaps(win32con.HORZRES)
                page_height = hDC.GetDeviceCaps(win32con.VERTRES)

                lines = text.splitlines()

                # Scale font height based on page height and number of lines
                font_height = int(page_height * 0.50)


                huge_font = win32ui.CreateFont({
                    "name": "Arial",
                    "height": font_height,
                    "weight": 700,
                })
                hDC.SelectObject(huge_font)


                total_height = len(lines) * font_height
                start_y = (page_height - total_height) // 2

                for i, line in enumerate(lines):
                    line_width, line_height = hDC.GetTextExtent(line)
                    x = (page_width - line_width) // 2
                    y = start_y + i * font_height
                    hDC.TextOut(x, y, line)

                hDC.EndPage()
                hDC.EndDoc()

            finally:
                # Always clean up the device context
                hDC.DeleteDC()

            return {"status": "printed"}

        except Exception as e:
            # Catch any unexpected errors
            return {"status": "error", "message": str(e)}, 500


if __name__ == "__main__":
    # Run with Waitress instead of Flask dev server
    serve(app, host="127.0.0.1", port=5000)
