#define MOTION_SENSOR A0

void myHandler(const char *event, const char *data);
int Controller(String command);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode( MOTION_SENSOR, INPUT );
  Particle.function("get", Controller);//html
}

void loop() {
  // put your main code here, to run repeatedly:
  if (digitalRead( MOTION_SENSOR ) == HIGH) {
      
      Particle.publish("motion",String(1), PRIVATE );//photon
      Serial.println("Active");
  }
  else {
    Particle.publish("motion",String(0), PRIVATE );
    Serial.println("Inactive");
  }
  delay(1000);
}

int Controller(String command)
{
    if (command == "run")
    {
        Particle.publish("Controller",String(1), PRIVATE );
        return 1;
    }
    if (command == "take")
    {
        
        Particle.publish("Controller",String(2), PRIVATE );
        return 1;
    }
    else if (command == "on")
    {
        Particle.publish("Controller",String(3), PRIVATE );
        return 1;
    }
    else if (command == "off")
    {
        Particle.publish("Controller",String(4), PRIVATE );
        return 1;
    }
    if (command == "clear")
    {
        Particle.publish("Controller",String(0), PRIVATE );
        return 1;
    }
    return -1;
}