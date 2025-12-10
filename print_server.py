from flask import Flask, request
from waitress import serve
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

            # --- Create a huge font ---
            huge_font = win32ui.CreateFont({
                "name": "Arial",
                "height": 800,   # very large text
                "weight": 700,   # bold
            })
            hDC.SelectObject(huge_font)

            # --- Center the text on the page ---
            page_width = hDC.GetDeviceCaps(win32con.HORZRES)
            page_height = hDC.GetDeviceCaps(win32con.VERTRES)

            lines = text.splitlines()
            total_height = len(lines) * 800
            start_y = (page_height - total_height) // 2

            for i, line in enumerate(lines):
                line_width, line_height = hDC.GetTextExtent(line)
                x = (page_width - line_width) // 2
                y = start_y + i * 800
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