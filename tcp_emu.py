from State import *
import socket
from sys import argv
import time#for sleep
import random
import re

IP = "127.0.0.1"
port = 5000

class Transition:
    def Closed(self):
        print("Error! Cannot Transition to Closed!")
        return False

    def Listen(self):#server
        print("Error! Cannot Transition to Listen!")
        return False

    def Syn_Recvd(self):#server
        print("Error! Cannot Transition to SYN/RECVD!")
        return False

    def Established(self):#server - client
        print("Error! Cannot Transition to Established!")
        return False

    def Close_Wait(self):#server
        print("Error! Cannot Transition to Close_Wait!")
        return False

    def Last_ACK(self):#server
        print("Error! Cannot Transition to Laast_ACK!")
        return False

    def SYN_Sent(self):#client
        print("Error! Cannot Transition to SYN_sent!")
        return False

    def Fin_Wait1(self):#client
        print("Error! Cannot Transition to Fin_Wait1!")
        return False

    def Fin_Wait2(self):#client
        print("Error! Cannot Transition to Fin_wait2!")
        return False

    def Timed_Wait(self):#client
        print("Error! Cannot Transition to idle!")
        return False


class Closed(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)
    
    def closed(self):
        print("Closed:closed")
        self.CurrentContext.Create_listen()#creates conection object for server
        self.CurrentContext.setState("listen")        
        return True

    def syn_sent(self):
        #only called when operating as a client
        #initiate connection process
        #and transition to connect state when connection made
        print("Closed:syn_sent")

        if self.CurrentContext.connection == 0:#only if in client
            print("creating client")
            try:            
                self.CurrentContext.make_connection()  
                synNum = "SYN " + str(random.randrange(90))
                print(f"syn number:{synNum}")
                self.CurrentContext.client_socket.send(str(synNum).encode())#sends sync number
                time.sleep(1)
                self.CurrentContext.setState("syn_sent")
            except:
                print("could not conect to server")        
        return True
        

    def trigger(self):
        #close open socket and reset object
        #return true if succeed. False otherwise
        print("Closed:trigger")
        try:
            print("closing socket")
            self.CurrentContext.serversocket.close()
            self.CurrentContext.addres = 0
            print("serer socket closed")
        except:
            try:
                self.CurrentContext.client_socket.close()
                self.CurrentContext.addres = 0
                print("client socet close")
            except:
                print("could not close socket")           
        return True

class Listen(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)
    
    def listen(self):
        while(True):#waits for a conection
            print("Listen:listen")
            self.CurrentContext.connection,self.CurrentContext.addres  = self.CurrentContext.serversocket.accept()#when someone conects
            print("-----------new connection-----------")
            print("connection from :" + str(self.CurrentContext.addres))
            data = self.CurrentContext.connection.recv(1024)
            data = data.decode()
            print(f"syn revced:{data}")

            tempNum = re.findall("\\d+",data)
            ackNum = "ACK " + str(int(tempNum[0]) + 1)

            synNum = "SYN " + str(random.randrange(90)) 
            print (f"syn:{synNum} | ack:{ackNum}")
            self.CurrentContext.connection.send(str(synNum).encode())
            time.sleep(2)
            self.CurrentContext.connection.send(str(ackNum).encode())            
            self.CurrentContext.setState("syn_recvd")
            time.sleep(1)
            return True        

    def trigger(self):
        print("Listen:trigger")
        self.listen()

class Syn_Recvd(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def syn_recvd(self):
        print("Syn_revcd:syn_recved")
        ackNum = self.CurrentContext.connection.recv(1024)
        ackNum = ackNum.decode()

        ackNum = re.findall("\\d+",ackNum)        

        print(f"revced ack:{ackNum}")
        self.CurrentContext.setState("established")
        return True

    def trigger(self):
        print("SYN_Revcd:trigger")
        self.syn_recvd()

class Established(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def established(self):
        data = ""
        try:#server            
            while (True):
                data = self.CurrentContext.connection.recv(1024)
                data = data.decode()

                out = re.search("^MSG",data)
                if (out):
                    print(data)
                elif (re.search("^FIN",data)):
                    break
                else:
                    print(f"unknown data recved:{data}")

            print("Fin recved|sending FIN ACK")
            self.CurrentContext.connection.send("FIN ACK".encode())
            time.sleep(1)
            self.CurrentContext.setState("close_wait")                

        except:#client
            #get close from user?
            while (data != "CLOSE"):
                print("enter data to send | use CLOSE to exit")
                data = input()
                if (data != "CLOSE"):#stops it from sending the close and only the fin
                    data = "MSG " + data
                    self.CurrentContext.client_socket.send(data.encode())
                    print(f"sent:{data}")

            print("Close | sending FIN")
            self.CurrentContext.client_socket.send("FIN".encode())
            time.sleep(1)
            self.CurrentContext.setState("fin_wait1")
        return True

    def trigger(self):
        print("Established:trigger")
        self.established()

class Close_Wait(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def close_wait(self):
        #close
        print("Close | sending FIN")
        self.CurrentContext.connection.send("FIN".encode())
        time.sleep(1)
        self.CurrentContext.setState("last_ack")
        return True

    def trigger(self):
        print("Close_Wait:trigger")
        self.close_wait()

class Last_ACK(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def last_ack(self):
        data = self.CurrentContext.connection.recv(1024)
        data = data.decode()
        print(f"fin ack revced:{data}")
        print("-----------demo end-----------")
        self.CurrentContext.setState("closed")
        return True

    def trigger(self):
        print("Last_ACK:trigger")
        self.last_ack()

class SYN_Sent(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def syn_sent(self):
        print ("SYN_Sent:syn_sent")
        syn = self.CurrentContext.client_socket.recv(1024)
        syn = syn.decode()
        if (re.search("^SYN",syn)):#syn revced
            ack = self.CurrentContext.client_socket.recv(1024)    
            ack = ack.decode()
            print(f"reved syn:{syn}|receved ack:{ack}")

            tempNum = re.findall("\\d+",ack)
            ack = "ACK " + str(int(tempNum[0]) + 1)
            
            print (f"sent ack:{ack}")
            self.CurrentContext.client_socket.send(str(ack).encode())
            time.sleep(1)
            self.CurrentContext.setState("established")
        
        elif (syn == "RST"):
            print ("rest")
            self.CurrentContext.setState("closed")

        else:
            print("timeout")
            self.CurrentContext.client_socket.send("RST".encode())
            self.CurrentContext.setState("closed")
        return True

    def trigger(self):
        print("Syn_sent:trigger")
        self.syn_sent()

class Fin_Wait1(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def fin_wait1(self):
        ack = self.CurrentContext.client_socket.recv(1024)
        ack = ack.decode()
        print(f"ack revced:{ack}")
        self.CurrentContext.setState("fin_wait2")
        return True

    def trigger(self):
        print("Fin_Wait1:trigger")
        self.fin_wait1()

class Fin_Wait2(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def fin_wait2(self):
        ack = self.CurrentContext.client_socket.recv(1024)
        ack = ack.decode()
        print(f"ack revced:{ack}")

        print("FIN ACK sent")

        self.CurrentContext.client_socket.send("FIN ACK".encode())
        time.sleep(1)
        self.CurrentContext.setState("timed_wait")
        return True

    def trigger(self):
        print("Fin_Wait2:trigger")
        self.fin_wait2()

class Timed_Wait(State, Transition):
    def __init__(self, Context):
        State.__init__(self, Context)

    def timed_wait(self):        
        time.sleep(1)
        print("time out")
        self.CurrentContext.setState("closed")
        return True

    def trigger(self):
        print("Timed_Wait:trigger")
        self.timed_wait()

class TCP(StateContext, Transition):
    def __init__(self):
        self.availableStates["closed"] = Closed(self)#server
        self.availableStates["listen"] = Listen(self)#server
        self.availableStates["syn_recvd"] = Syn_Recvd(self)#server
        self.availableStates["established"] = Established(self)#server - client
        self.availableStates["close_wait"] = Close_Wait(self)#server
        self.availableStates["last_ack"] = Last_ACK(self)#server
        self.availableStates["syn_sent"] = SYN_Sent(self)#client
        self.availableStates["fin_wait1"] = Fin_Wait1(self)#client
        self.availableStates["fin_wait2"] = Fin_Wait2(self)#client
        self.availableStates["timed_wait"] = Timed_Wait(self)#client
        self.setState("closed")#delfult state

        self.connection = 0
        self.addres = 0
        
    def closed(self):
        return self.CurrentState.closed()
    def listen(self):
        return self.CurrentState.listen()
    def syn_recvd(self):
        return self.CurrentState.syn_recvd()
    def established(self):
        return self.CurrentState.established()
    def close_wait(self):
        return self.CurrentState.close_wait()
    def last_ack(self):
        return self.CurrentState.last_ack()
    def syn_sent(self):
        return self.CurrentState.syn_sent()
    def fin_wait1(self):
        return self.CurrentState.fin_wait1()
    def fin_wait2(self):
        return self.CurrentState.fin_wait2()
    def timed_wait(self):
        return self.CurrentState.timed_wait()

    def Create_listen(self):
        '''this method initiates a listen socket'''
        self.serversocket = socket.socket()
        self.serversocket.bind((IP,port))
        self.serversocket.listen(1)#allows 1 conection

    def make_connection(self):
        '''this method initiates an outbound connection'''
        print("make connection")
        self.client_socket =  socket.socket()
        self.client_socket.connect((IP,port))
        self.connection = IP

if __name__ == '__main__':
    if len(argv) < 2:
        print("Error: too few arguments")
        exit()
    ActivePeer = TCP()    
    if argv[1] == "server":
        print("Server")
        ActivePeer.closed()
    else:
        print("client")
        ActivePeer.syn_sent()