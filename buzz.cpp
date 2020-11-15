#include "Alarms.h"

void alarmPatternComposer();
void patternDecode(uint8_t resource,uint16_t first,uint16_t second,uint16_t third,uint16_t cyclepause, uint16_t endpause);
void setTiming(uint8_t resource, uint16_t pulse, uint16_t pause);
void turnOff(uint8_t resource);
void toggleResource(uint8_t resource, uint8_t activate);
void vario_output(uint16_t d, uint8_t up);
void inline switch_led_flasher(uint8_t on);
void inline switch_landing_lights(uint8_t on);
void PilotLampSequence(uint16_t speed, uint16_t pattern, uint8_t num_patterns);

static uint8_t cycleDone[5]={0,0,0,0,0}, 
               resourceIsOn[5] = {0,0,0,0,0};
static uint32_t LastToggleTime[5] ={0,0,0,0,0};
static int16_t  i2c_errors_count_old = 0;

static uint8_t SequenceActive[5]={0,0,0,0,0};

#if defined(BUZZER)
  uint8_t isBuzzerON(void) { return resourceIsOn[1]; } // returns true while buzzer is buzzing; returns 0 for silent periods
#else
  uint8_t isBuzzerON() { return 0; }
#endif  //end of buzzer define
/********************************************************************/
/****                      Alarm Handling                        ****/
/********************************************************************/
/*
AlarmArray
0: toggle
1: failsafe
2: noGPS
3: beeperOn
4: pMeter
5: runtime
6: vBat
7: confirmation
8: Acc
9: I2C Error
*/
/*
Resources:
0: Buzzer

*/
void alarmHandler(void){
  
  #if defined(RCOPTIONSBEEP)
    static uint8_t i = 0,firstrun = 1, last_rcOptions[CHECKBOXITEMS];
                  
    if (last_rcOptions[i] != rcOptions[i])   alarmArray[ALRM_FAC_TOGGLE] = ALRM_LVL_TOGGLE_1;
      last_rcOptions[i] = rcOptions[i]; 
      i++;
    if(i >= CHECKBOXITEMS)i=0;
    
    if(firstrun == 1 && alarmArray[ALRM_FAC_CONFIRM] == ALRM_LVL_OFF) {
      alarmArray[ALRM_FAC_TOGGLE] = ALRM_LVL_OFF;    //only enable options beep AFTER gyro init
      alarmArray[ALRM_FAC_BEEPERON] = ALRM_LVL_OFF;
    }        
    else firstrun = 0;
  #endif  
     
  #if defined(FAILSAFE)
    if ( failsafeCnt > (5*FAILSAFE_DELAY) && f.ARMED) {
      alarmArray[ALRM_FAC_FAILSAFE] = ALRM_LVL_FAILSAFE_PANIC;                                                                   //set failsafe warning level to 1 while landing
      if (failsafeCnt > 5*(FAILSAFE_DELAY+FAILSAFE_OFF_DELAY)) alarmArray[ALRM_FAC_FAILSAFE] = ALRM_LVL_FAILSAFE_FINDME;          //start "find me" signal after landing
    }
    if ( failsafeCnt > (5*FAILSAFE_DELAY) && !f.ARMED) alarmArray[ALRM_FAC_FAILSAFE] = ALRM_LVL_FAILSAFE_FINDME;                  // tx turned off while motors are off: start "find me" signal
    if ( failsafeCnt == 0) alarmArray[ALRM_FAC_FAILSAFE] = ALRM_LVL_OFF;                                              // turn off alarm if TX is okay
  #endif
  
  #if GPS
    if ((f.GPS_mode != GPS_MODE_NONE) && !f.GPS_FIX) alarmArray[ALRM_FAC_GPS] = ALRM_LVL_GPS_NOFIX;
    else if (!f.GPS_FIX) alarmArray[ALRM_FAC_GPS] = ALRM_LVL_ON;
    else alarmArray[ALRM_FAC_GPS] = ALRM_LVL_OFF;
  #endif
  
  #if defined(BUZZER)
    if ( rcOptions[BOXBEEPERON] ) alarmArray[ALRM_FAC_BEEPERON] = ALRM_LVL_ON;
    else alarmArray[ALRM_FAC_BEEPERON] = ALRM_LVL_OFF;
  #endif

  #if defined(POWERMETER)
    if ( (pMeter[PMOTOR_SUM] < pAlarm) || (pAlarm == 0) || !f.ARMED) alarmArray[ALRM_FAC_PMETER] = ALRM_LVL_OFF;
    else if (pMeter[PMOTOR_SUM] > pAlarm) alarmArray[ALRM_FAC_PMETER] = ALRM_LVL_ON;
  #endif 
  
  #if defined(ARMEDTIMEWARNING)
    if (ArmedTimeWarningMicroSeconds > 0 && armedTime >= ArmedTimeWarningMicroSeconds && f.ARMED) alarmArray[ALRM_FAC_RUNTIME] = ALRM_LVL_ON;
    else alarmArray[ALRM_FAC_RUNTIME] = ALRM_LVL_OFF;
  #endif
  
  #if defined(VBAT)
    if (vbatMin < conf.vbatlevel_crit) alarmArray[ALRM_FAC_VBAT] = ALRM_LVL_VBAT_CRIT;
    else if ( (analog.vbat > conf.vbatlevel_warn1)  || (NO_VBAT > analog.vbat)) alarmArray[ALRM_FAC_VBAT] = ALRM_LVL_OFF;
    else if (analog.vbat > conf.vbatlevel_warn2) alarmArray[ALRM_FAC_VBAT] = ALRM_LVL_VBAT_INFO;
    else if (analog.vbat > conf.vbatlevel_crit) alarmArray[ALRM_FAC_VBAT] = ALRM_LVL_VBAT_WARN;
    //else alarmArray[6] = 4;
  #endif
  
  if (i2c_errors_count > i2c_errors_count_old+100 || i2c_errors_count < -1) alarmArray[ALRM_FAC_I2CERROR] = ALRM_LVL_ON;
  else alarmArray[ALRM_FAC_I2CERROR] = ALRM_LVL_OFF;
  #if defined(LCD_TELEMETRY) && !defined(SUPPRESS_TELEMETRY_PAGE_8)
    if (telemetry == 8) lcd_telemetry(); // must output the alarms states now because alarmPatternComposer() will reset alarmArray[]
  #endif
  alarmPatternComposer();
}

void alarmPatternComposer(){ 
  static char resource = 0;
  // patternDecode(length1,length2,length3,beeppause,endpause,loop)
  #if defined(BUZZER)
    resource = 1;                                                                                  //buzzer selected
    if      ( IS_ALARM_SET(ALRM_FAC_FAILSAFE , ALRM_LVL_FAILSAFE_FINDME) )       patternDecode(resource,200,0,0,50,2000);                       //failsafe "find me" signal
    else if ( IS_ALARM_SET(ALRM_FAC_FAILSAFE , ALRM_LVL_FAILSAFE_PANIC) ||
                IS_ALARM_SET(ALRM_FAC_ACC , ALRM_LVL_ON) ) patternDecode(resource,50,200,200,50,50); //failsafe "panic"  or Acc not calibrated
    else if ( IS_ALARM_SET(ALRM_FAC_TOGGLE , ALRM_LVL_TOGGLE_1) ) patternDecode(resource,50,0,0,50,0);           //toggle 1
    else if ( IS_ALARM_SET(ALRM_FAC_TOGGLE , ALRM_LVL_TOGGLE_2) ) patternDecode(resource,50,50,0,50,0);          //toggle 2
    else if ( IS_ALARM_SET(ALRM_FAC_TOGGLE , ALRM_LVL_TOGGLE_ELSE) )  patternDecode(resource,50,50,50,50,0);     //toggle else
    #if GPS
      else if ( IS_ALARM_SET(ALRM_FAC_GPS , ALRM_LVL_GPS_NOFIX) ) patternDecode(resource,50,50,0,50,50);         //gps installed but no fix
    #endif
    else if ( IS_ALARM_SET(ALRM_FAC_BEEPERON , ALRM_LVL_ON) )  patternDecode(resource,50,50,50,50,50);           //BeeperOn
    #ifdef POWERMETER
      else if ( IS_ALARM_SET(ALRM_FAC_PMETER , ALRM_LVL_ON) ) patternDecode(resource,50,50,0,50,120);              //pMeter Warning
    #endif
    else if ( IS_ALARM_SET(ALRM_FAC_RUNTIME , ALRM_LVL_ON) ) patternDecode(resource,50,50,50,50,0);              //Runtime warning
    #ifdef VBAT
      else if ( IS_ALARM_SET(ALRM_FAC_VBAT , ALRM_LVL_VBAT_CRIT) ) patternDecode(resource,50,50,200,50,2000);      //vbat critical
      else if ( IS_ALARM_SET(ALRM_FAC_VBAT , ALRM_LVL_VBAT_WARN) ) patternDecode(resource,50,200,0,50,2000);       //vbat warning
      else if ( IS_ALARM_SET(ALRM_FAC_VBAT , ALRM_LVL_VBAT_INFO) ) patternDecode(resource,200,0,0,50,2000);        //vbat info
    #endif
    else if ( IS_ALARM_SET(ALRM_FAC_CONFIRM , ALRM_LVL_CONFIRM_1) ) patternDecode(resource,200,0,0,50,200);      //confirmation indicator 1x
    else if ( IS_ALARM_SET(ALRM_FAC_CONFIRM , ALRM_LVL_CONFIRM_2) ) patternDecode(resource,200,200,0,50,200);    //confirmation indicator 2x
    else if ( IS_ALARM_SET(ALRM_FAC_CONFIRM , ALRM_LVL_CONFIRM_ELSE) ) patternDecode(resource,200,200,200,50,200); //confirmation indicator 3x
    else if (SequenceActive[(uint8_t)resource] == 1) patternDecode(resource,0,0,0,0,0);                   // finish last sequence if not finished yet
    else turnOff(resource);                                                                        // turn off the resource 
    alarmArray[ALRM_FAC_ACC] = ALRM_LVL_OFF;                                                                             //reset acc not calibrated
    
  #endif
  
  
}

void patternDecode(uint8_t resource,uint16_t first,uint16_t second,uint16_t third,uint16_t cyclepause, uint16_t endpause){
  static uint16_t pattern[5][5];
  static uint8_t icnt[5] = {0,0,0,0,0};
  
  if(SequenceActive[resource] == 0){
    SequenceActive[resource] = 1; 
    pattern[resource][0] = first; 
    pattern[resource][1] = second;
    pattern[resource][2] = third;
    pattern[resource][3] = endpause;
    pattern[resource][4] = cyclepause;
  }
  if(icnt[resource] <3 ){
    if (pattern[resource][icnt[resource]] != 0){
      setTiming(resource,pattern[resource][icnt[resource]],pattern[resource][4]);
     }
  }
  else if (LastToggleTime[resource] < (millis()-pattern[resource][3]))  {  //sequence is over: reset everything
    icnt[resource]=0;
    SequenceActive[resource] = 0;                               //sequence is now done, cycleDone sequence may begin
    alarmArray[ALRM_FAC_TOGGLE] = ALRM_LVL_OFF;                                //reset toggle bit
    alarmArray[ALRM_FAC_CONFIRM] = ALRM_LVL_OFF;                                //reset confirmation bit
    turnOff(resource);   
    return;
  }
  if (cycleDone[resource] == 1 || pattern[resource][icnt[resource]] == 0) {            //single on off cycle is done
    if (icnt[resource] < 3) {
      icnt[resource]++;
    }
    cycleDone[resource] = 0;
    turnOff(resource);    
  }  
}




/********************************************************************/
/****                   Global Resource Handling                 ****/
/********************************************************************/

  void setTiming(uint8_t resource, uint16_t pulse, uint16_t pause){
    if (!resourceIsOn[resource] && (millis() >= (LastToggleTime[resource] + pause))&& pulse != 0) {
      resourceIsOn[resource] = 1;      
      toggleResource(resource,1);
      LastToggleTime[resource]=millis();      
    } else if ( (resourceIsOn[resource] && (millis() >= LastToggleTime[resource] + pulse) ) || (pulse==0 && resourceIsOn[resource]) ) {
      resourceIsOn[resource] = 0;
      toggleResource(resource,0);
      LastToggleTime[resource]=millis();
      cycleDone[resource] = 1;     
    } 
  } 
 
  void toggleResource(uint8_t resource, uint8_t activate){
     switch(resource) {     
        #if defined (BUZZER)   
          case 1:
            if (activate == 1) {BUZZERPIN_ON;}
            else BUZZERPIN_OFF;
            break; 
      
      }
      return;
  }





