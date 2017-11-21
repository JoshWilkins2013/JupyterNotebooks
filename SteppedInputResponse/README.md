# Step Responses

Given a stepped input (such as a step and hold temperature ramp), the output 
at the 'hold' regions are captured. This script will plot the input and output 
with these regions. Requires two csv files (file names Input.csv and Output.csv) 
each with their own MJD times in the first column and the data in the second column. 
The script returns two csv files; The averaged results and the transient responses.