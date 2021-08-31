# ------------------------------------------------------------------------------------------
#    Alunos:        William Felipe Tsubota          - 2017.1904.056-7
#                   Marllon Lucas Rodrigues Rosa    - 2017.1904.045-1
#                   Gabriel C. M.                   - 2017.1904.005-2
#                               
#                              Trabalho 1
#    
#    Professora:    Hana Karina Salles Rubinsztejn
# ------------------------------------------------------------------------------------------

#!/usr/bin/env python3
import socket
import sys
import threading
import time
import reader as read
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

class Proxy(object):
    """Class responsible for interfacing the client with the server"""

    def __init__(self, port, max_conn, buffer_size, inputpath='blacklist.txt'):
        self.listening_port = port
        self.max_conn = max_conn
        self.buffer_size = buffer_size
        self.size = 0
        self.tam_cache = 73400320
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # Variable of connection
        self.conn = 0
        self.addr = ""
        # Variable of the data
        self.data = ""

        # get list from reader.py > inputpath
        reader = read.reader()
        self.blackList = reader.createList(inputpath)

        # dic for data
        self.x = {}

        # dict for information of cache elements
        self.y = {}

        # time in sec (epoch)
        self.start_time = time.time()

        # for log
        self.result = ''
        dd = datetime.now() + timedelta(seconds=30) # lancamento do primeiro log
        self.scheduler.add_job(self.writeArchive, 'date', run_date=dd, kwargs={})
        print('pronto pra criar o log')

        try:
            # Initialize browser connection socket
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serverSocket.bind(('', self.listening_port))
            self.serverSocket.listen(self.max_conn)

            print("[*] Initializing Sockets ... Done")
            print("[*] Sockets Binded Successfully")
            print("[*] Server Started Successfully [ %d ]\n" % (self.listening_port))

        except Exception as e:
            print("[*] Unable to initialise socket")
            sys.exit(2)

        while True:
            try:
                # Establish the connection
                (client_socket, client_address) = self.serverSocket.accept()

                # Create a new thread for a new request
                thread = threading.Thread(target=self.proxy_thread, args=(client_socket, client_address))
                thread.setDaemon(True)
                thread.start()

            except Exception as e:
                self.serverSocket.close()
                print("\n[*] Proxy Server Shuting Down ...")
                sys.exit(1)

    def isGet(self, request, client_socket):
        method = request.split(b' ')[0]
        if method == b'GET':
            print("Sucess!")
            return True
        elif method == b'':
            return False
        else:
            client_socket.send(b'<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">HTTP/1.1 501 Not Implemented\r\n\r\n</pre></body></html>')
            #client_socket.send(b'HTTP/1.1 501 Not Implemented\r\n\r\n') # proprio navegador, o de cima eh o escrito em html
            print("Erro: Não implementado (501)")
            self.result += 'HTTP/1.1 501 Not Implemented\n'
            return False

    def delete_in_cache(self, url):
        self.size = self.size - self.y[url][-1]
        del (self.x[url])
        del (self.y[url])
        print('apaguei da cache o link ' + url)
        print(self.size)

    def writeArchive(self):
        if(self.result != ''):
            args = "logs//" + time.ctime(time.time()) + ".txt"
            args = args.replace(':', ';')

            arq = open(args, 'w+')
            arq.write(self.result)
            arq.close()
            self.result = ''
            print('log criado')
        else:
            print('log nao criado')
        dd = datetime.now() + timedelta(seconds=30) # lancamento dos logs subsequentes
        self.scheduler.add_job(self.writeArchive, 'date', run_date=dd, kwargs={})
        pass

    def proxy_thread(self, client_socket, client_address):

        # Get browser request
        request = client_socket.recv(self.buffer_size)

        if (self.isGet(request, client_socket)):

            # Get webserver and port of connection
            webserver, port, temp = self.get_data(request.decode())

            decoded_request = request.decode()
            separator = "User-Agent:"
            request1, request2 = decoded_request.split(separator)
            request1 = request1 + "Connection: Close\r\n"
            request2 = "User-Agent:" + request2
            decoded_request = request1 + request2

            # print(decoded_request)

            request = decoded_request.encode()

            #################################################################
            # AQUI IRA A MANIPULACAO DA BLACKLIST                           #
            # ONDE VERIFICAMOS SE O WEBSERVER REQUISITADO PODE SER ACESSADO #
            #################################################################

            # Can I connect in this server?
            connect = True

            for posicao in self.blackList:
                if (
                        posicao == 'http://' + webserver or posicao == 'http://' + webserver + '/' or posicao == webserver or posicao == webserver + '/'):
                    connect = False
                    print("\n[*] URL In Blacklist Aborting ...")
                    self.result += '[*] ' + webserver +' In Blacklist Aborting ...\n'

            if(datetime.now().hour*60 + datetime.now().minute > int(0)*60 + int(00) and 
                datetime.now().hour*60 + datetime.now().minute < int(6)*60 + int(00)):
                connect = False
                print("\n[*] URL Blocked due to the schedule ...")
                self.result += '[*] ' + webserver +' Blocked due to the schedule ...\n'

            # If i can connect in the server i do
            if connect:

                #################################################################
                # TENHO QUE VERIFICAR SE A CONEXAO EM QUE EU ESTOU REQUISITANDO #
                # JA ESTA EM MINHA ESTRUTURA DE DADOS, CASO NAO ESTEJA EU BAIXO #
                # OS DADOS PARA MEU SERVIDOR E ARMAZENO NA MINHA ESTRUTURA      #
                # CASO EU TENHA OS DADOS EU DEVO APENAS CARREGAR ELES E ENVIAR  #
                # PARA O MEU NAVEGADOR!                                         #
                #################################################################

                if temp in self.x.keys():
                    # Recive the data of the server
                    for i in range(len(self.x[temp])):
                        reply = self.x[temp][i]
                        #print(reply)

                        if (len(reply) > 0):
                            # Send the data to browser
                            client_socket.send(reply)

                            # Example of message
                            dar = float(len(reply))
                            dar = float(dar / 1024)
                            dar = "%.3s" % (str(dar))
                            dar = "%s KB" % dar

                            print("[*] Request Done in cache: %s => %s <=" % (temp, str(dar)))
                            self.result+='[*] Request Done in cache: %s => %s <=' % (temp, str(dar))+'\n'


                else:
                    try:
                        # Do connect of webserver
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((webserver, port))
                        s.send(request)
                        cache_provisoria = []

                        # time of recv data and put in cache
                        current = time.time()
                        # total bytes of file
                        size = 0

                        while True:
                            # Receive the data of the server
                            reply = s.recv(buffer_size)
                            #print(reply)

                            # print(len(reply))

                            size = size + len(reply)

                            if (len(reply) > 0):
                                # Send the data to browser
                                client_socket.send(reply)

                                # Example of message
                                dar = float(len(reply))
                                dar = float(dar / 1024)
                                dar = "%.3s" % (str(dar))
                                dar = "%s KB" % dar

                                print("[*] Request Done NOC: %s => %s <=" % (temp, str(dar)))
                                self.result+='[*] Request Done NOC: %s => %s <=' % (temp, str(dar))+'\n'

                                cache_provisoria.append(reply)

                            else:
                                # client_socket.send("\r\n\r\n")
                                if temp not in self.x.keys():
                                    self.x[temp] = []
                                while (self.tam_cache < (size + self.size)):
                                    key = list(self.y.keys())[0]
                                    self.size = self.size - self.y[key][-1]
                                    del (self.x[key])
                                    del (self.y[key])

                                self.x[temp] = cache_provisoria
                                dd = datetime.now() + timedelta(seconds=300)
                                self.scheduler.add_job(self.delete_in_cache, 'date', run_date=dd, kwargs={'url': temp})
                                self.size = self.size + size

                                self.y[temp] = [current, size]
                                print(self.y[temp])

                                print(self.size)
                                print('adicionado : ' + temp)
                                break

                        s.close()
                        client_socket.close()

                    except Exception as e:
                        s.close()
                        client_socket.close()
                        sys.exit(1)

    def get_data(self, data):

        # Get first line of data requisition
        first_line = data.split("\n")[0]
        # get url
        url = first_line.split(" ")[1]

        # Get a position of "HTTP"
        http_pos = url.find("://")

        # Get the complete URL
        temp = url if (http_pos == -1) else url[(http_pos + 3):]

        # Get position port
        port_pos = temp.find(":")
        # Get position server
        webserver_pos = temp.find("/")

        if (webserver_pos == -1):
            webserver_pos = len(temp)

        webserver = ""
        port = -1

        if (port_pos == -1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]

        # Returns webserver end por of requisition
        print('web server: ' + webserver + ' temp: ' + temp)

        return webserver, port, temp


if __name__ == '__main__':
    try:
        listening_port = int(input("[*] Enter Listening Por Number: "))
        max_conn = 5
        buffer_size = 8192

        Proxy(listening_port, max_conn, buffer_size)

    except KeyboardInterrupt:
        print("\n[*] User Requested An Interrupt")
        print("[*] Application Exiting ...")
        sys.exit()
