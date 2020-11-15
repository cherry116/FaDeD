#include "Alarms.h"


 
  
  /************************************************************************************************************/
  /****************************                Cam stabilize Servos             *******************************/

  #if defined(SERVO_TILT)
    servo[0] = get_middle(0);
    servo[1] = get_middle(1);
    if (rcOptions[BOXCAMSTAB]) {
      servo[0] += ((int32_t)conf.servoConf[0].rate * att.angle[PITCH]) /50L;
      servo[1] += ((int32_t)conf.servoConf[1].rate * att.angle[ROLL])  /50L;
    }
  #endif

  #ifdef SERVO_MIX_TILT
    int16_t angleP = get_middle(0) - MIDRC;
    int16_t angleR = get_middle(1) - MIDRC;
    if (rcOptions[BOXCAMSTAB]) {
      angleP += ((int32_t)conf.servoConf[0].rate * att.angle[PITCH]) /50L;
      angleR += ((int32_t)conf.servoConf[1].rate * att.angle[ROLL])  /50L;
    }
    servo[0] = MIDRC+angleP-angleR;
    servo[1] = MIDRC-angleP-angleR;
  #endif

/****************                    Cam trigger Servo                ******************/
  #if defined(CAMTRIG)
    // setup MIDDLE for using as camtrig interval (in msec) or RC channel pointer for interval control
    #define CAM_TIME_LOW  conf.servoConf[2].middle
    static uint8_t camCycle = 0;
    static uint8_t camState = 0;
    static uint32_t camTime = 0;
    static uint32_t ctLow;
    if (camCycle==1) {
      if (camState == 0) {
        camState = 1;
        camTime = millis();
      } else if (camState == 1) {
        if ( (millis() - camTime) > CAM_TIME_HIGH ) {
          camState = 2;
          camTime = millis();
          if(CAM_TIME_LOW < RC_CHANS) {
            ctLow = constrain((rcData[CAM_TIME_LOW]-1000)/4, 30, 250);
            ctLow *= ctLow;
          } else ctLow = CAM_TIME_LOW;
        }
      } else { //camState ==2
        if (((millis() - camTime) > ctLow) || !rcOptions[BOXCAMTRIG] ) {
          camState = 0;
          camCycle = 0;
        }
      }
    }
    if (rcOptions[BOXCAMTRIG]) camCycle=1;
    servo[2] =(camState==1) ? conf.servoConf[2].max : conf.servoConf[2].min;
    servo[2] = (servo[2]-1500)*SERVODIR(2,1)+1500;
  #endif
}
