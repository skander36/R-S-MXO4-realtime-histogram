
# R&S-MXO4-realtime-histogram

This is a python script which can grab data from R&S MXO4 scope to draw histogram of a measured parameter with pyplot and seaborn.
It is a bit slow-ish, maybe I can found a better solution in the future. But this is a temporary solution until R&S introduce this function into the firmware. Until now (FW. ver 2.8.2.0) it is not available as far as I know.
The measurement can be changed in script at line 20  "... meas_type=MeasType.FREQuency".
The list of measurements of amplitude/time can be found in user manual (page 1005):
HIGH | LOW | AMPLitude | MAXimum | MINimum | PDELta |
MEAN | RMS | STDDev | CRESt | POVershoot | NOVershoot |
AREA | RTIMe | FTIMe | PPULse | NPULse | PERiod | FREQuency
| PDCYcle | NDCYcle | CYCarea | CYCMean | CYCRms
| CYCStddev | CYCCrest | CAMPlitude | CMAXimum | CMINimum
| CPDelta | PULCnt | DELay | PHASe | BWIDth | EDGecount
| SETup | HOLD | SHT | SHR | DTOTrigger | SLERising |
SLEFalling
Not all measures are useful to be histogramed, sa one cand delete from them at line 28.
Also the ip address must be chnaged on line 10.
An AI improved code - faster (did not wait for OPC) with trackin window.

<img width="989" height="628" alt="Screenshot 2026-01-15 154108" src="https://github.com/user-attachments/assets/bc6fc33c-dc98-4517-9fe0-246ee2192a6b" />


<img width="1394" height="892" alt="IA version" src="https://github.com/user-attachments/assets/f9e13cc4-07fc-4eba-baa8-308156ad4d1d" />
