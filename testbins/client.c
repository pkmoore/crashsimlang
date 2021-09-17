
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
    
int sock;
sock=socket(AF_INET,SOCK_STREAM,0);
struct sockaddr_in server_address;
server_address.sin_family=AF_INET;
//server_address.sin_port=htons(8001);
server_address.sin_port=0;
server_address.sin_addr.s_addr=inet_addr("192.168.1.100");;

int connection=connect(sock,(struct sockaddr *) &server_address,
sizeof(server_address));
if (connection==-1){
    printf("there is an issue");
}
char server_response[256];
recv(sock,&server_response,sizeof(server_response),0);
printf("the server response is %s\n", server_response);
close(sock);
return 0;
}

	

