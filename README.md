
# R-S-MXO4-realtime-histogram

This is a python script which can grab data from R&S MXO4 scope to draw histogram of a measured parameter with pyplot.
The parameter can be changed in script at line 20  "... meas_type=MeasType.FREQuency".
The list of measurements of amplitude/time can be found in user manual (page 1005):
HIGH | LOW | AMPLitude | MAXimum | MINimum | PDELta |
MEAN | RMS | STDDev | CRESt | POVershoot | NOVershoot |
AREA | RTIMe | FTIMe | PPULse | NPULse | PERiod | FREQuency
| PDCYcle | NDCYcle | CYCarea | CYCMean | CYCRms
| CYCStddev | CYCCrest | CAMPlitude | CMAXimum | CMINimum
| CPDelta | PULCnt | DELay | PHASe | BWIDth | EDGecount
| SETup | HOLD | SHT | SHR | DTOTrigger | SLERising |
SLEFalling


<img width="989" height="628" alt="Screenshot 2026-01-15 154108" src="https://github.com/user-attachments/assets/bc6fc33c-dc98-4517-9fe0-246ee2192a6b" />
