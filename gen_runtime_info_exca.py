'''
Create runtime information for excavation as follows:
    1)  generate a pool of locations (2d coordinates) based on the arm's reachable area.
        Please refer to TODO for the arm's reachable area.
    2)  given numbers of excavation and dump locations, randomly draw from the pool.
    3)  for each excavation location, randomly draw a number in [0, 1] as its science
        value and make its excavatability probability inversely proportional to its
        science value to make the planning problem interesting.
'''

import os
import sys
import random
import json
import matplotlib.pyplot as plt


def gen_loc_pool(x_gap=0.2, y_gap=0.1, debug=True):
    loc_pool = []
    y_steps = int(2/y_gap)
    for y_step in range(0, y_steps+1):
        y = round(1 - y_gap*y_step, 4)
        y_abs = abs(y)
        x_low = 1 + (0.45 + (0.55-0.45)*(1-y_abs))
        x_up  = 1 + (1.2 - 0.6*y_abs)
        x_steps = int((x_up - x_low) / x_gap)
        for x_step in range(0, x_steps+1):
            x = round(x_low + x_gap*x_step, 4)
            loc_pool.append((x, y))

    if debug:
        loc_pool.sort(key = lambda x: x[1])
        print("Number of locations in the pool: " + str(len(loc_pool)))
        print(loc_pool)

    return loc_pool

class RuntimeInfoExcaGenerator():
    def __init__(self, loc_pool, debug=True):
        self.loc_pool = loc_pool
        self.debug = debug

    # Science value (SV) and excavatiability probaility
    def getExProb(self, sv):
        beta = 0.4
        return 1-beta*sv

    def getSVs(self, num_of_locs):
        sci_vals = []
        for i in range(num_of_locs):
            sci_vals.append(random.random())
        return sci_vals

    def gen_runtime_info(self, xloc_num=10, dloc_num=6, runtime_info_fp="runtime_info_exca.json"):
        locs = random.sample(self.loc_pool, xloc_num+dloc_num)
        xloc_list = locs[:xloc_num]
        dloc_list = locs[xloc_num:]

        if self.debug:
            print("\nList of " + str(xloc_num) + " excavation locations:")
            print(xloc_list)
            print("\nList of " + str(dloc_num) + " dump locations:")
            print(dloc_list)

            print("\nCreating a scatter plot for excavation and dump locations.\n")
            loc_x_plt = [loc[0] for loc in xloc_list]
            loc_y_plt = [loc[1] for loc in xloc_list]
            plt.scatter(loc_x_plt, loc_y_plt, c="coral", label="Exca Loc")
            loc_x_plt = [loc[0] for loc in dloc_list]
            loc_y_plt = [loc[1] for loc in dloc_list]
            plt.scatter(loc_x_plt, loc_y_plt, c="lightblue", label="Dump Loc")
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.title("The spread of excavation and dump locations.")
            plt.legend()
            scatter_plot_fp = runtime_info_fp[:-4] + "jpg"
            plt.savefig(scatter_plot_fp)

        runtime_info = {"scenario": "excavation", 'xloc_list': {}, 'dloc_list': {}}


        sci_vals = self.getSVs(xloc_num)
        ex_probs = [self.getExProb(sv) for sv in sci_vals]

        for xloc, loc_idx in zip(xloc_list, range(1, xloc_num+1)):
            xloc_ID = "xloc"+str(loc_idx)
            xloc_obj = {
                    "name": xloc_ID,
                    "position": {"x":xloc[0], "y":xloc[1]},
                    "sci_val": sci_vals[loc_idx-1],
                    "ex_prob": ex_probs[loc_idx-1]
                    }
            runtime_info["xloc_list"][xloc_ID] = xloc_obj


        for dloc, loc_idx in zip(dloc_list, range(1, dloc_num+1)):
            dloc_ID = "dloc"+str(loc_idx)
            dloc_obj = {
                    "name": dloc_ID,
                    "position": {"x":dloc[0], "y":dloc[1]},
                    }
            runtime_info["dloc_list"][dloc_ID] = dloc_obj

        with open(runtime_info_fp, "w") as outfile: 
            json.dump(runtime_info, outfile)

##################
def main(argv):
	print("args:"+str(argv)+"\n")

        runtime_info_fp = argv[0]
        xloc_num = int(argv[1])
        dloc_num = int(argv[2])

        loc_pool = gen_loc_pool(x_gap=0.2, y_gap=0.1)

        runtime_info_generator = RuntimeInfoExcaGenerator(loc_pool)
        runtime_info_generator.gen_runtime_info(xloc_num, dloc_num, runtime_info_fp)

if __name__ == "__main__":
   main(sys.argv[1:])
