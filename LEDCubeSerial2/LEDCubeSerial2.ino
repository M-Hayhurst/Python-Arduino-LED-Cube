/* 
 *  Run a 3x3x3 LED cube and receive new patterns and settings from a computer over the serial connection.
 *  Author: Martin Hayhurst Appel
 *  Email: martin.ledzep@gmail.com
 */
 
// Definitions. Define the digital outputs which turn the levels on and off
#define L1 11
#define L2 12
#define L3 13 
#define MAXFRAMES 250

// The LED columns are pins 2 to 10 inclusive. Pin 1 is discouraged as it is a serial port.

// Define global varibles
int n_frames; // number of frames in the current animation
byte cur_pat[MAXFRAMES*4]; // current pattern to be played. Each frame consumes 4 bytes 
bool run = true; // animation only runs if true. Can be set to zero to enable serial com without loss
int cur_frame = 0; // number of current frame

int FRAMEDURATION = 200; // appriximate duration of frame in ms
int LEVELDURATION = 1; // duration of single level in ms
int DUTYCYCLE = 50; //duty cycle as a percentage. Lower dutycycle gives dimmer LEDs. This is implemented by having a dark delay after cycling through all 3 levels.

int DARKTIME = 0; // derived quantity related to DUTYCYCLE, LEVELDURATION and FRAMEDURATION.
int FRAMEREPS = 0;

// define hardcoded patterns
bool default_pat[] = {1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1}; 
int default_n_frames = 9;

void setup() {
  // initialize digital pins as outputs.
  for(int i=2; i<14; i++)
  {
    pinMode(i, OUTPUT);
  }

  // begin serial
  Serial.begin(9600);

  // load the default pattern into memory
  load_default_pattern();
  update_timings();
}

void load_default_pattern(){
  n_frames = default_n_frames;
  for (int n=0; n<default_n_frames; n++) // loop over frames
  {
    for (int i=0; i<27; i++) // loop over the 27 bools in the frame
    {
      bitWrite(cur_pat[n*4+i/8], i%8, default_pat[n*27+i]);
    }
  }
    
}

void update_timings(){
  // calculate the delay after showing a frame and the number of blinks in order to achieve a given dutycycle and a given frame duration
  DARKTIME = round(3*LEVELDURATION*(100/DUTYCYCLE - 1));
  FRAMEREPS = ceil(FRAMEDURATION/(3*LEVELDURATION + DARKTIME)); 
}

void turnoff_levels(){
  // turn the requested level on and the others off. Zero indexed
  digitalWrite(L1, LOW);
  digitalWrite(L2, LOW);
  digitalWrite(L3, LOW);
}

void turnon_level(int n){
  digitalWrite(11+n, HIGH);
}

void show_frame(byte *pat){
  // make the cube show a single frame 
  // Takes a pointer to a place in an array with 3*9 consecutive boolean values
  for(int i=0; i<3; i++){
    turnoff_levels();
    for(int j=0; j<9; j++){
      digitalWrite(2+j, bitRead(pat[(i*9+j)/8], (i*9+j)%8) );
    }
    turnon_level(i);
    delay(LEVELDURATION);
  }
  turnoff_levels();
  delay(DARKTIME);
}

// the loop function runs over and over again forever
void loop() {
  if(run){
    for (int i=0; i<FRAMEREPS; i++)
    {
      show_frame(cur_pat+4*cur_frame);
    }
    cur_frame = (cur_frame+1)%n_frames;
  }
}

void serialEvent(){
    while (Serial.available()){
      char c = Serial.read(); // read the first char of the buffer
      Serial.write(c);

      switch (c) {
        case 'G': // confirm connection, just return the same character
          break;

        case 'S': // stop animation
          run = false;
          break;

        case 'R': // resume animation
          run = true;
          break;

        case 'N': // set number of frames
        {
          long n;
          n = Serial.readStringUntil('\n').toInt();
          Serial.println(n);
          if (n>0 && n<=MAXFRAMES){ // ensure n can never be so large, that a new pattern overwrites the pattern array.
            n_frames = n;
          }
          break;
        }

        case 'D': // set dutycycle
        {
          long d;
          d = Serial.readStringUntil('\n').toInt();
          Serial.println(d);
          if (d>0 && d<=100){
            DUTYCYCLE = d;
          }
          update_timings();
          break;
        }

        case 'T': // set frame duration
        {
          long T;
          T = Serial.readStringUntil('\n').toInt();
          Serial.println(T);
          if (T>10 && T<=10000){
            FRAMEDURATION = T;
          }
          update_timings();
          break;
        }

        case 'O': // reset pattern to built in
        load_default_pattern();
        break;
        
        case 'P': //receive pattern
        {
          Serial.readBytes(cur_pat, n_frames*4);
          char c = Serial.read();
          if (c == '\n')
          {
            Serial.println("New Pattern read succesfully.");
          }
          else{
            Serial.println("Did not reveice expected newline when reading binary pattern.");
          }
          break;
        }

        case 'H': //Help! Print varibles
        {
          Serial.println("nFrames");
          Serial.println(n_frames);

          Serial.println("FRAMEDURATION");
          Serial.println(FRAMEDURATION);
          
          Serial.println("LEVELDURATION");
          Serial.println(LEVELDURATION);
          
          Serial.println("DUTYCYCLE");
          Serial.println(DUTYCYCLE);
          
          Serial.println("DARKTIME");
          Serial.println(DARKTIME);
          
          Serial.println("FRAMEREPS");
          Serial.println(FRAMEREPS);
          
          Serial.println("run");
          Serial.println(run);
          
          Serial.println("cur_frame");
          Serial.println(cur_frame);

          Serial.println("END");

        }

        default:
          Serial.write('?');
          break;  
      }
    
    }
}

