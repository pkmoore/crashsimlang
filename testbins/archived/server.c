
#include<stdio.h>
#include<string.h> //strlen
#include<stdlib.h> //strlen
#include<unistd.h> //strlen
#include<sys/types.h>
#include<sys/socket.h>

#include<arpa/inet.h> //inet_addr
#include<netinet/in.h> //inet_addr

int main(int argc , char *argv[])
{

char server_message[256]="message from server";
int server_sock;
server_sock=socket(AF_INET,SOCK_STREAM,0);

struct sockaddr_in server_address;
server_address.sin_family=AF_INET;
server_address.sin_port = 0;
server_address.sin_addr.s_addr=inet_addr("192.168.1.100");

bind(server_sock,(struct sockaddr*) &server_address,
sizeof(server_address));
listen (server_sock,5);
int client_socket;
client_socket=accept(server_sock,NULL,NULL);
send(client_socket,server_message,sizeof(server_message),0);
close(server_sock);
return 0;
}

	

