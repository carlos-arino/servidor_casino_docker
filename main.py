# crupier de blackjack por mqtt
import paho.mqtt.client as mqtt
import json
import random

class crupier:
    "" "Administrar una baraja completa de cartas y ser capaz de repartir"""
    def __init__(self):

        self.cartas = ["A","K","Q","J",10 ,9 ,8 , 7,6 ,5 , 4 , 3 ,2]

    def get_carta(self):
        return random.choice(self.cartas)
    def get_valor(self,cartas):
        suma = 0
        A = 0
        for carta in cartas:
            if isinstance(carta,str):
                valor = 10
                if (carta =="A"):
                    valor += 1
                    A += 1
            else:
                valor = carta
            suma += valor
        while (suma > 21) and (A>0):
            suma -= 10
            A -= 1
        return suma

casino = dict()
reglas = crupier()

def convertir_tabla(estado):
    output = []

    for key in estado:
        obj = {"nombre": key}
        for subkey in estado[key]:
            if isinstance(estado[key][subkey], list):
                 obj[subkey] = ",".join(str(x) for x in estado[key][subkey])
            else:
                 obj[subkey] = estado[key][subkey]
        output.append(obj)
    return output

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))
    # Print result of connection attempt
    client.subscribe("instrumentacion/blackjack") 
    # Subscribe to the topic “digitest/test1”, receive any messages  published on it


def on_message(client, userdata, msg):  # The callback for when a PUBLISH   message is received from the server.
    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    relacion = json.loads(msg.payload)
    jugador = relacion['jugador']
    mesa = dict()
    if (relacion['accion']=="nueva"):
        if  not(jugador in casino):
            casino[jugador] = dict()
            casino[jugador]['partidas'] = 1
            casino[jugador]['ganadas'] = 0
            casino[jugador]['fondos'] = 79
        else:
            casino[jugador]['partidas'] += 1
            casino[jugador]['fondos'] -= 1
        casino[jugador]['crupier'] = [reglas.get_carta()]
        casino[jugador]['jugador'] = [reglas.get_carta()]
        casino[jugador]['jugador'].append(reglas.get_carta())
        casino[jugador]['estado'] = "activa"

    if (relacion['accion'] == "carta") and (jugador in casino):
        if casino[jugador]['estado'] == "activa":
            casino[jugador]['jugador'].append(reglas.get_carta())
            if (reglas.get_valor(casino[jugador]['jugador']) > 21):
                casino[jugador]['estado'] = "perdiste"
            else:
                casino[jugador]['estado'] = "activa"

    if (relacion['accion'] == "planto") and (jugador in casino):
        if casino[jugador]['estado'] == "activa":
            while (reglas.get_valor(casino[jugador]['crupier']) < 17):
                casino[jugador]['crupier'].append(reglas.get_carta())
            if (reglas.get_valor(casino[jugador]['crupier'])> 21):
                casino[jugador]['estado'] = "ganaste"
                casino[jugador]['ganadas'] += 1
                casino[jugador]['fondos'] += 2
            elif (reglas.get_valor(casino[jugador]['crupier'])<reglas.get_valor(casino[jugador]['jugador'])):
                casino[jugador]['estado'] = "ganaste"
                casino[jugador]['ganadas'] += 1
                casino[jugador]['fondos'] += 2
            elif (reglas.get_valor(casino[jugador]['crupier'])==reglas.get_valor(casino[jugador]['jugador'])):
                casino[jugador]['estado'] = "empate"
                casino[jugador]['fondos'] += 1
            else:
                casino[jugador]['estado'] = "perdiste"


    if jugador in casino:
        mapped_crupier = map(str, casino[jugador]['crupier'])
        mapped_jugador = map(str, casino[jugador]['jugador'])
        mesa['crupier'] = " ".join(mapped_crupier)
        mesa['jugador'] = " ".join(mapped_jugador)
        mesa['estado'] = casino[jugador]['estado']
        mesa['fondos'] = casino[jugador]['fondos']
        client.publish("instrumentacion/"+jugador,json.dumps(mesa),retain=True)
        print (casino)
        client.publish("instrumentacion/estado_casino",json.dumps(convertir_tabla(casino)),retain=True)


client = mqtt.Client("digi_mqtt_test")  # Create instance of client with client ID “digi_mqtt_test”
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.connect("test.mosquitto.org", 1883)
# client.connect("broker.emqx.io", 1883)
client.loop_forever()  # Start networking daemon
