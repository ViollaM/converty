import asyncio
import shlex
from cowsay import cowsay, list_cows

clients = {}
available_cows = list_cows()

async def chat(reader, writer):
    me = ""
    is_registered = False
    
    buffer = asyncio.Queue()
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(buffer.get())
    
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                message = q.result().decode().split()
                
                if len(message) < 1:
                    continue
                else:
                    match message:
                        case ['who']:
                            writer.write(f"Registered users: {', '.join(clients.keys())}\n".encode())
                            await writer.drain()
                        case ['cows']:
                            writer.write(f"Available cows: {', '.join(list_cows())}\n".encode())
                            await writer.drain()
                        case ['login', name]:
                            if not is_registered:
                                if name in available_cows:
                                    me = name
                                    print("Registered: ", me)
                                    clients[me] = asyncio.Queue()
                                    available_cows.remove(name)
                                    writer.write("Registration succeed.\n".encode())
                                    await writer.drain()
                                    is_registered = True
                                    receive.cancel()
                                    receive = asyncio.create_task(clients[me].get())
                                else:
                                    writer.write("Wrong name, try another one.\n".encode())
                                    await writer.drain()
                                    continue
                        case ['say', user, text]:
                            if is_registered:
                                if user in clients.keys():
                                    await clients[user].put(f"From: {me}\n {cowsay((' '.join(text)).strip(), cow=me)}")
                                    writer.write("Message successfully send.\n".encode())
                                    await writer.drain()
                                else:
                                    writer.write(f"User with name {user} not found.\n".encode())
                                    await writer.drain()
                            else:
                                writer.write("You need log in to start chatting.\n".encode())
                                await writer.drain()
                                continue
                        case ['yield', text]:
                            if is_registered:
                                for out in clients.values():
                                    if out is not clients[me]:
                                        await out.put(f"From: {me}\n {cowsay(' '.join(text).strip(), cow=me)}")
                                writer.write("Message successfully send.\n".encode())
                                await writer.drain()
                            else:
                                writer.write("You need log in to start chatting.\n".encode())
                                await writer.drain()
                                continue
                        case ['quit']:
                            receive.cancel()
                            send.cancel()
                            if is_registered:
                                del clients[me]
                                print("Unregistered: ", me)
                                available_cows.append(me)
                            writer.close()
                            await writer.wait_closed()
                            return
                        case [*_]:
                            writer.write("Unknown command.\n".encode())
                            await writer.drain()
                            continue
            elif q is receive and is_registered:
                receive = asyncio.create_task(clients[me].get())
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()
    send.cancel()
    receive.cancel()
    print("Unregistered: ", me)
    del clients[me]
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
