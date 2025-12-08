import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd
from matplotlib.backend_bases import MouseEvent
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from cie2000 import CIEDE2000
import sys









def lab_color_parallel(l,a,b):
    return LabColor(l,a,b)


lab_color_parallel = np.vectorize(lab_color_parallel)


def line_lab(ax, b, L, ITA,categories, positions, ita_levels):
    CS = ax.contour(b, L, ITA, levels=ita_levels, colors='black', linewidths=1.2,linestyles='dashed')
    ax.clabel(CS, inline=True, fontsize=8, fmt='%1.0f°')

    for (label, lab), (Lpos, bpos) in zip(categories, positions):
    # convert to RGB
        rgb = convert_color(lab, sRGBColor).get_value_tuple()

        # Draw the swatch
        ax.scatter(
            Lpos,bpos,
            color=rgb,
            s=200,
            linewidth=1.2,
            marker='s',   # "s" = square, use "o" for circle
            alpha=.2
        )

        ax.scatter(
            Lpos,bpos,
            color=rgb,
            s=100,
            linewidth=1.2,
            edgecolor="black",
            marker='s'   # "s" = square, use "o" for circle
        )
        

        # Optionally add the text label
        ax.text(
            Lpos+2, bpos ,
            label,
            fontsize=12,
            va='center'
        )


def plot_L_vs_b( ax, filename, back=True, title_prefix="Skin Tone Analysis", alpha=1.0, size=100, edgecolor='black'):
    """
    Plot L* vs a* and L* vs b* side by side for palette colors and input RGB.
    """
    data = np.loadtxt("assets/"+filename,delimiter=",")
    if data.shape == (6,):
        data = data.reshape((1,6))
    if back:
        input_lab = lab_color_parallel(data[:,0],data[:,1],data[:,2])
    else : 
        input_lab = lab_color_parallel(data[:,3],data[:,4],data[:,5])

    for i in range(len(input_lab)):
        lab = input_lab[i]
        rgb = convert_color(lab, sRGBColor).get_value_tuple()
        ax.scatter(lab.lab_b, lab.lab_l, color=[c for c in rgb], edgecolor=edgecolor, s=size,alpha=alpha)

    # ax.text(lab_input.lab_a, lab_input.lab_l + 2,
    #         f"Input\nL*={lab_input.lab_l:.1f}, a*={lab_input.lab_a:.1f}",
    #         ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_xlabel("b*  (blue–yellow)")
    ax.set_ylabel("L* (lightness)")
    ax.set_title(f"{title_prefix} — N={len(input_lab)}")
    ax.set_xlim(0, 65)
    ax.set_ylim(10, 100)
    ax.grid(True, alpha=0.3)
    
    # Plot L* vs b*
    ax.grid(True, alpha=0.3)
    # ax.set(adjustable='box')
    # ax.set_box_aspect(1)   
    
    

files=["Lab_Black.csv",  "Lab_East_Asian.csv",  "Lab_LatinX.csv",  "Lab_MiddleEastern.csv",  "Lab_Mixed.csv",  "Lab_North_African.csv",  "Lab_South_Asian.csv",  "Lab_Southeast_Asian.csv",  "Lab_White.csv", "Lab_All_Ethnicities.csv"]
names=["Black Skin Tone","East Asian Skin Tone","Latin Skin Tone","Middle Eastern Skin Tone","Mixed Race Skin Tone","North African Skin Tone","South Asian Skin Tone","Southeast Asian Skin Tone","White Skin Tone","All Skin Tone"]

categories = [
    ("Dark",         LabColor(40, 20, 20)),
    ("Brown",        LabColor(55, 15, 20)),
    ("Tan",          LabColor(65, 10, 20)),
    ("Intermediate", LabColor(75, 5,  10)),
    ("Light",        LabColor(85, 2,   5)),
    ("Very Light",   LabColor(95, 0,   2)),
]

# Coordinates where swatches should appear
positions = [
    (30, 20),   # Dark
    (40, 40),   # Brown
    (40, 64),   # Tan
    (40, 80),   # Intermediate
    (35, 90),   # Light
    (10, 90),   # Very Light (custom location)
]
L_grid = np.linspace(10, 100, 200)
b_grid = np.linspace(0, 65, 200)
L, b = np.meshgrid(L_grid, b_grid)
ITA = np.degrees(np.arctan2(L - 50, b))
ita_levels = [-30, 10, 28, 41, 55]
contour_labels = ["Dark", "Brown", "Tan", "Intermediate", "Light", "Very Light"]

fig, axs = plt.subplots(3,3, figsize=(10, 10))
for i in range(3):
    for j in range(3):
        index = i*3 + j
        if index < len(files)-1:
            plot_L_vs_b( axs[i,j], "Lab_All_Ethnicities.csv", back=True, alpha=0.15,edgecolor='none')

            plot_L_vs_b( axs[i,j], files[index], back=True, title_prefix=names[index]+ " Back hand")
            line_lab(axs[i,j], b, L, ITA,categories, positions, ita_levels)
            

plt.tight_layout()

fig3, axs3 = plt.subplots(3,3, figsize=(10, 10))
for i in range(3):
    for j in range(3):
        index = i*3 + j
        if index < len(files)-1:
            plot_L_vs_b( axs3[i,j], "Lab_All_Ethnicities.csv", back=False, alpha=0.15,edgecolor='none')

            plot_L_vs_b( axs3[i,j], files[index], back=False, title_prefix=names[index]+ " Front hand")
            line_lab(axs3[i,j], b, L, ITA,categories, positions, ita_levels)
            
plt.tight_layout()

fig2, ax2 = plt.subplots(1,2, figsize=(18, 6))
plot_L_vs_b( ax2[0], "Lab_All_Ethnicities.csv", back=True, title_prefix="All Skin Tone"+ " Back hand")
line_lab(ax2[0], b, L, ITA,categories, positions, ita_levels)

plot_L_vs_b( ax2[1], "Lab_All_Ethnicities.csv", back=False, title_prefix="All Skin Tone"+ " Front hand")
line_lab(ax2[1], b, L, ITA,categories, positions, ita_levels)

plt.show()