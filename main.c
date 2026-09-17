#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "lwip/sockets.h"
#include "esp_netif.h"
#include "esp_http_client.h"
#include "cJSON.h"



#define WIFI_SSID   "_____" //The Network name the device should connect to
#define WIFI_PASS   "_____" //Password to that network
#define SBC_IP      "_____" //Ip of Main SBC
#define MAXIMUM_RETRY   5


/*Json Packet Structure*/
/*
{
"Device_ID":    "Module_1",
"Checksum":     "_________",
"Timestamp":    "XX:XX",
"Addresser":    "_________",
"Checksum_2"    "_________",
"Type"          "Message/Word/Float",
},
"messages": {
"Sender_ID":    "",
"Message":      "",
},
"word": {
"DataParse1":   "",
"DataParse2":   "",
"DataParse3":   "",
"DataParse4":   "",
},
"float": {
"Array"     "",
}





*/
//How we will handle word sending between the devices, purely message or text
struct wordpacket {
uint8_t ID;
uint8_t Checksum;
uint8_t Timestamp;
uint8_t Addresser;
uint8_t DataParse1;
uint8_t DataParse2;
uint8_t DataParse3;
uint8_t DataParse4;
uint8_t Checksum_2;
};

//How we will handle float packets
struct floatpacket{
uint8_t ID;
uint8_t Checksum;
uint8_t Timestamp;
uint8_t Addresser;
float array[16];
uint8_t Checksum_2;
};


//Message packet
struct messagepacket{
uint8_t ID;
uint8_t Checksum;
uint8_t Timestamp;
char sender_ID[32];
char message[256];
uint8_t Addresser;
uint8_t Checksum_2;
};

//Initialize the wifi module
void wifi_init_sta(void)
{

}

//The wifi handler
static void wifi_event_handler()
{

}

static void bluetooth_event_handler()
{

}

//The setup for the device connected to the esp32
void setup(void)
{

}

//The real time protocol changer, ie. bluetooth wifi long range wifi etc
void protocol_change(void)
{

}

//As everything needs to be sent via tcp protocol
void tcp_server_task(void *arg)
{

}

//For when it receives packets from the SBC
void receive(void)
{
    
}

//For when it sends packets back to the SBC
void relay(void)
{

}

//Main 
void app_main(void)
{

}