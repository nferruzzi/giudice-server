#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
import http.server
import threading
import socketserver
import ui


class WebService (http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send message back to client
        message = "Presente"

        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))


    def do_POST(self):
        self.send_response(200)


class Controller (object):
    def listen(self):
        print("listening")
        server_address = ('', 8000)
        self.httpd = socketserver.TCPServer(server_address, WebService)
        self.httpd.serve_forever()
        print("done listening")

if __name__ == '__main__':
    controller = Controller()

    tr = threading.Thread(target=controller.listen)
    tr.start()

    app = QApplication(sys.argv)
    w = QMainWindow()

    main_window = ui.Ui_MainWindow()
    main_window.setupUi(w)

    #w.resize(250, 150)
    #w.move(300, 300)
    #w.setWindowTitle('Simple')
    w.show()
    v = app.exec_()
    controller.httpd.shutdown()
    sys.exit(v)
