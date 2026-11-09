#include <WiFi.h>
#include <ArduinoJson.h>

// Replace with your mobile hotspot credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Password expected by the data glove
const String VALID_PASSWORD = "GloveSecretPass123";

WiFiServer wifiServer(5000);

// XOR checksum matching Python's reduce(operator.xor, data.encode(), 0)
int calculateXorChecksum(String data) {
  int checksum = 0;
  for (int i = 0; i < data.length(); i++) {
    checksum ^= (int)data[i];
  }
  return checksum;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connect to Wi-Fi hotspot
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected successfully!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // Start TCP Server on port 5000
  wifiServer.begin();
  Serial.println("TCP Server started on port 5000.");
}

void loop() {
  WiFiClient client = wifiServer.available();

  if (client) {
    Serial.println("Client connected.");
    
    while (client.connected()) {
      if (client.available()) {
        // Read incoming line-buffered JSON from your friend's script
        String incomingLine = client.readStringUntil('\n');
        incomingLine.trim();

        if (incomingLine.length() > 0) {
          StaticJsonDocument<512> doc;
          DeserializationError error = deserializeJson(doc, incomingLine);

          if (error) {
            Serial.print("JSON deserialization failed: ");
            Serial.println(error.c_str());
            break;
          }

          // Extract password attempt from nested schema
          const char* clientMessage = doc["messages"]["Message"];
          Serial.print("Received password attempt: ");
          Serial.println(clientMessage);

          bool isAuthorized = (clientMessage != nullptr && String(clientMessage) == VALID_PASSWORD);
          String responseMsg = isAuthorized ? "Accepted" : "Incorrect Password";
          int respChecksum = calculateXorChecksum(responseMsg);

          // 1. Build and send primary response with static timestamp & exact JSON layout
          StaticJsonDocument<512> responseDoc;
          responseDoc["Device_ID"] = "PDG";
          responseDoc["Checksum"] = respChecksum;
          responseDoc["Timestamp"] = "2026-11-09 15:00:00"; 
          responseDoc["Addresser"] = "";
          responseDoc["Checksum2"] = respChecksum; 
          responseDoc["Type"] = "Message";

          JsonObject msgObj = responseDoc.createNestedObject("messages");
          msgObj["Sender_ID"] = WiFi.localIP().toString();
          msgObj["Message"] = responseMsg;

          String responseString;
          serializeJson(responseDoc, responseString);
          client.println(responseString);

          // 2. If authorized, send the secondary sensor data packet
          if (isAuthorized) {
            delay(50); 
            
            StaticJsonDocument<512> shakeDoc;
            shakeDoc["Device_ID"] = "PDG";
            shakeDoc["Checksum"] = 100;
            shakeDoc["Timestamp"] = "2026-11-09 15:00:01";
            shakeDoc["Addresser"] = "";
            shakeDoc["Checksum2"] = 100;
            shakeDoc["Type"] = "Sensor_Data";

            JsonObject sensorObj = shakeDoc.createNestedObject("messages");
            sensorObj["Flex_1"] = 850;
            sensorObj["Flex_2"] = 430;

            String shakeString;
            serializeJson(shakeDoc, shakeString);
            client.println(shakeString);
          }
        }
      }
    }
    client.stop();
    Serial.println("Client disconnected.");
  }
}