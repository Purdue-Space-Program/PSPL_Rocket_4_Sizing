import matplotlib.pyplot as plt
import math
import numpy as np
from scipy import interpolate



#In degrees
discharge_angle = 15

def calc_blade_profile(discharge_angle, inlet_angle, outer_diam, inlet_diam):
    radii = []
    n = 11
    for i in range(n+1):
        radii.append(0.5*((i)*(outer_diam-inlet_diam)/n+inlet_diam))

    thetas = []
    Rs = []
    for i in range(len(radii)):
        theta = (i*(discharge_angle-inlet_angle)/n+inlet_angle)
        thetas.append(theta)

    B1 = [thetas[i] for i in range(len(thetas)) if i%2==0]
    B2 = [thetas[i] for i in range(len(thetas)) if (i%2==0 and i>=2) or i==11]
    R1 = [radii[i] for i in range(len(radii)) if i%2==0]
    R2 = [radii[i] for i in range(len(radii)) if (i % 2 == 0 and i >= 2) or i == 11]

    print(B1)
    print(B2)
    print(R1)
    print(R2)
    print("_____")
    for i in range(len(B1)):
        R = 0.5 * ((R2[i])**2 - (R1[i])**2) / (
                (R2[i]) * math.cos(B2[i]*math.pi/180) - (R1[i]) * math.cos(B1[i]*math.pi/180))
        Rs.append(R)
    print(Rs)

    start_x, start_y = inlet_diam/2*math.cos(math.pi), inlet_diam/2*math.sin(math.pi)
    CX1, CY1 = Rs[0]*math.cos(B1[0]*math.pi/180)+start_x, Rs[0]*math.sin(B1[0]*math.pi/180)+start_y
    CX = [CX1]
    CY = [CY1]
    X = [start_x]
    Y = [start_y]
    
    for i in range(20):
        angle_sum = 0
        for j in range(1, i+2):
            print(j)
            angle_sum += B1[j]
        x_p = Rs[i]*math.cos((180-angle_sum+B1[0])*math.pi/180)+CX[i]
        y_p = Rs[i]*math.sin((180-angle_sum+B1[0])*math.pi/180)+CY[i]
        X.append(x_p)
        Y.append(y_p)
        cx_i = -1*Rs[i+1]*math.cos((180-angle_sum+B1[0])*math.pi/180)+x_p
        cy_i = -1*Rs[i+1]*math.sin((180-angle_sum+B1[0]) * math.pi / 180)+y_p
        CX.append(cx_i)
        CY.append(cy_i)
        if (x_p**2+y_p**2)>=(outer_diam/2)**2: break
    return X, Y



def plot_blades(num_blades, X, Y, outlet_diam, inlet_diam):
    #Convert X, Y to polar
    BladeRadii = []
    BladeAngles = []
    for j in range(num_blades):
        PointRadii = []
        PointAngles = []
        for i in range(len(X)):
            PointRadii.append(math.sqrt(X[i]**2+Y[i]**2))
            temp_angle = math.atan(Y[i]/X[i])
            if Y[i]/X[i]>0: temp_angle += math.pi
            PointAngles.append(temp_angle+j*(2*math.pi/num_blades))
        BladeRadii.append(PointRadii)
        BladeAngles.append(PointAngles)

    print(">>>>>")
    AllX = []
    AllY = []
    for r in range(len(BladeRadii)):
        x_coords = []
        y_coords = []
        for i in range(len(BladeRadii[r])):
            x_coords.append(BladeRadii[r][i]*math.cos(BladeAngles[r][i]))
            y_coords.append(BladeRadii[r][i]*math.sin(BladeAngles[r][i]))
        tck, u = interpolate.splprep([x_coords, y_coords], s=0)
        x_, y_ = interpolate.splev(np.linspace(0, 1, 100), tck, der=0)
        AllX.append(x_)
        AllY.append(y_)

    figure, axes = plt.subplots()
    for i in range(len(AllX)):
        axes.plot(AllX[i], AllY[i], c='blue', linewidth=2.0)
        axes.scatter(AllX[i][0], AllY[i][0], s=3, c='red')

    for i in range(len(X)+2):
        if i%2==0 or i==7:
            c = plt.Circle((0, 0), i*(outlet_diam-inlet_diam)/(2*num_blades)+inlet_diam/2, fill=False)
            axes.add_artist(c)
    axes.set_aspect(1)

    axes.set_xlim([-25, 25])
    axes.set_ylim([-25, 25])
    plt.show()


outer_diam = 0.84 #inches
inlet_diam = 0.368 #inches

outer_diam *= 25.4
inlet_diam *= 25.4

print(outer_diam)

X, Y = calc_blade_profile(29, 18, outer_diam, inlet_diam)

print(X)
print(Y)
plot_blades(5, X, Y, outer_diam, inlet_diam)
