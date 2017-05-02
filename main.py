import socket
import template
import time
import machine

HOSTP = ('0.0.0.0', 80)


PIN_R = 14
PIN_G = 12
PIN_B = 13



class LedControl:

    def __init__(self, pin_r, pin_g, pin_b):
        self.pin_r = machine.PWM(machine.Pin(pin_r), freq = 50)
        self.pin_g = machine.PWM(machine.Pin(pin_g), freq = 50)
        self.pin_b = machine.PWM(machine.Pin(pin_b), freq = 50)

        self.valor_r = 0
        self.valor_g = 0
        self.valor_b = 0
        self.valor_random = 'OFF'

    def set(self, r, g, b):
        self.valor_r = int(r)
        self.valor_g = int(g)
        self.valor_b = int(b)
        self.duty()

    def duty(self):
        self.pin_r.duty(self.conversion(self.valor_r))
        self.pin_g.duty(self.conversion(self.valor_g))
        self.pin_b.duty(self.conversion(self.valor_b))

    def conversion(self, n):
        return int((float(n) / 255) * 1000)

    def randomcolor(self):
        r = 1000
        g = 0
        b = 0
        self.set(r, g, b)
        while self.valor_random == 'ON' or 'On' or 'on':
            time.sleep(1)
            if r > 0 and b == 0:
                r -= 4
                g += 4
            if g > 0 and r == 0:
                g -= 4
                b += 4
            if b > 0 and g == 0:
                b -= 4
                r += 4
            print(r, g, b)
            self.set(r, g, b)

    def extraer_url(self, file: object):
        while True:
            line = file.readline().decode()
            print(line)
            if not line or line == '\r\n':
                break
            if line.startswith('GET'):
                diccionariovalores = {}

                listaurl = line.split()[1][2:].split('&')
                try:
                    for i in listaurl:
                        n = i.split('=')
                        diccionariovalores[n[0]] = n[1]
                except:
                    pass

                if diccionariovalores.keys():
                    self.cambiarvalores(diccionariovalores)
                    break

    def cambiarvalores(self, diccionario):
        for i in diccionario.keys():
            if i == 'r' and diccionario['random'] == 'OFF' or 'Off' or 'off':
                self.valor_r = diccionario[i]
            if i == 'g'and diccionario['random'] == 'OFF' or 'Off' or 'off':
                self.valor_g = diccionario[i]
            if i == 'b' and diccionario['random'] == 'OFF' or 'Off' or 'off':
                self.valor_b = diccionario[i]
            if i == 'random':
                self.valor_random = diccionario[i]
                self.randomcolor()

    def crear_socket(self, HOST):

        s = socket.socket()
        s.bind(HOST)
        s.listen(2)

        while True:
            cl, addr = s.accept()
            print("Cliente Conectado desde :", addr)
            cl_file = cl.makefile('rb', 0)

            self.extraer_url(cl_file)

            reponse = 'HTTP/1.1 200 OK\n'
            reponse += 'Content-Type: text/html\n'
            reponse += template.html % (self.valor_r, self.valor_g, self.valor_b, self.valor_random)

            total_send = 0
            while total_send < len(reponse[total_send:]):
                send = cl.send(reponse[total_send:].encode('utf-8'))
                if send == 0:
                    raise RuntimeError('Socket connection broken')
                total_send += send
            cl.close()

new = LedControl(PIN_R, PIN_G, PIN_B)
new.crear_socket(HOSTP)