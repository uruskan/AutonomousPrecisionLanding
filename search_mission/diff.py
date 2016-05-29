import math

pi = 3.14159
epsilon = 0.000000001
tmax = 2*pi
tmin = 0

x = 0.0
y = 0.0
v_x = 0.0
v_y = 0.0

def pos(t):
	x = 40*math.cos(t)/(math.sin(t)*math.sin(t)+1)
	y = 20*math.sin(2*t)/(math.sin(t)*math.sin(t)+1)	

def vel(t):
	d_x = (40*math.sin(t)*math.sin(t)*math.sin(t)-120*math.sin(t))/((1+math.sin(t)*math.sin(t))*(1+math.sin(t)*math.sin(t)))
	d_y = (40-120*math.sin(t)*math.sin(t))/((1+math.sin(t)*math.sin(t))*(1+math.sin(t)*math.sin(t)))

def Speed(t):
	return (40/(math.sqrt(1+math.sin(t)*math.sin(t))))


def arcLength(t):
	dT = 0.001
	integral = 0
	time = 0.0	
	
	while(time<=t):
		integral += Speed(time)*dT
		time += dT
	

	return integral



def GetCurveParameter(s):

	Lmax = arcLength(tmax);
	t = tmin + (s*(tmax-tmin))/Lmax
	
	print "Lmax = ", Lmax
	lower = tmin
	upper = tmax
	i = 0
	imax = 1000
	for i in range(0,imax):
	
		F = arcLength(t) - s
		if (abs(F) < epsilon):
		
			return t
		

		DF = Speed(t)
		tCandidate = t - F/DF

		if(F>0):
		
			upper = t
			if(tCandidate <= lower):
			
				t = 0.5*(upper+lower)
	
			
			else:
				t = tCandidate
			
		
		else: 
			lower = t
			if (tCandidate >= upper):
				t = 0.5*(upper+lower);
			
			else:	
				t = tCandidate
		
	return t



print "s value: "
s = float(raw_input())
Lmax = arcLength(tmax)

if s > Lmax:
	s_new = s%Lmax
	print "s_new ", s_new

t = GetCurveParameter(s_new)
print "The corresponding t value is ", t	


