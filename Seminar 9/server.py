import socket

HOST        = '127.0.0.1'
PORT        = 9999
BUFFER_SIZE = 1024

clienti_conectati = {}
mesaje = {} 
id_contor = 0

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("=" * 50)
print(f"  SERVER UDP pornit pe {HOST}:{PORT}")
print("  Asteptam mesaje de la clienti...")
print("=" * 50)

while True:
    try:
        date_brute, adresa_client = server_socket.recvfrom(BUFFER_SIZE)
        mesaj_primit = date_brute.decode('utf-8').strip()

        parti = mesaj_primit.split(' ', 1)
        comanda = parti[0].upper()
        argumente = parti[1] if len(parti) > 1 else ''

        print(f"\n[PRIMIT] De la {adresa_client}: '{mesaj_primit}'")

        if comanda == 'CONNECT':
            if adresa_client in clienti_conectati:
                raspuns = "EROARE: Esti deja conectat la server."
            else:
                clienti_conectati[adresa_client] = True
                nr_clienti = len(clienti_conectati)
                raspuns = f"OK: Conectat cu succes. Clienti activi: {nr_clienti}"
                print(f"[SERVER] Client nou conectat: {adresa_client}")

        elif comanda == 'DISCONNECT':
            if adresa_client in clienti_conectati:
                del clienti_conectati[adresa_client]
                raspuns = "OK: Deconectat cu succes. La revedere!"
                print(f"[SERVER] Client deconectat: {adresa_client}")
            else:
                raspuns = "EROARE: Nu esti conectat la server."

        elif comanda in ['PUBLISH', 'DELETE', 'LIST']:
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Trebuie sa fii conectat la server pentru aceasta comanda. Foloseste CONNECT."
            
            elif comanda == 'PUBLISH':
                if not argumente:
                    raspuns = "EROARE: Mesajul nu poate fi gol."
                else:
                    id_contor += 1
                    mesaje[id_contor] = {'text': argumente, 'autor': adresa_client}
                    raspuns = f"OK: Mesaj publicat cu ID={id_contor}"
                    print(f"[SERVER] Mesaj publicat de {adresa_client}: {argumente} (ID={id_contor})")

            elif comanda == 'DELETE':
                try:
                    msg_id = int(argumente)
                    if msg_id in mesaje:
                        if mesaje[msg_id]['autor'] == adresa_client:
                            del mesaje[msg_id]
                            raspuns = "OK: Mesaj sters cu succes."
                            print(f"[SERVER] Mesaj ID={msg_id} sters de {adresa_client}")
                        else:
                            raspuns = "EROARE: Nu esti autorul acestui mesaj."
                    else:
                        raspuns = f"EROARE: Mesajul cu ID={msg_id} nu exista."
                except ValueError:
                    raspuns = "EROARE: ID-ul mesajului trebuie sa fie un numar intreg."

            elif comanda == 'LIST':
                if not mesaje:
                    raspuns = "OK: Nu exista mesaje publicate."
                else:
                    lista_mesaje = [f"{mid}: {m['text']}" for mid, m in mesaje.items()]
                    raspuns = "OK:\n" + "\n".join(lista_mesaje)

        else:
            raspuns = f"EROARE: Comanda '{comanda}' este necunoscuta. Comenzi valide: CONNECT, DISCONNECT, PUBLISH, DELETE, LIST"

        server_socket.sendto(raspuns.encode('utf-8'), adresa_client)
        print(f"[TRIMIS]  Catre {adresa_client}: '{raspuns}'")

    except KeyboardInterrupt:
        print("\n[SERVER] Oprire server...")
        break
    except Exception as e:
        print(f"[EROARE] {e}")

server_socket.close()
print("[SERVER] Socket inchis.")
