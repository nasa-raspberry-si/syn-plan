'''
This script simulates the excavation scenario except executing the new PLEXIL plan.
It contains 4 steps as follows:
    1) Synthesize runtime information: lists of excavation and dump locations.
    2) Generate a PRISM model based on the synthesized runtime information.
    3) Use PRISM model to extract policy and a plan, e.g., selected excavation and dump locations.
    4) Plan Translation: translate the synthesized plan to a PLEXIL plan.
'''

import os
import sys
import random
import json
import shutil
from subprocess import Popen, PIPE

from argparse import ArgumentParser

from gen_runtime_info_exca import RuntimeInfoExcaGenerator, gen_loc_pool
from gen_prism_model import PrismGenerator
from plexil_plan_translator import PlexilPlanTranslator


# Currently only max_tried=1 is supported.
#
# When faulty_ex_prob == -1, it means no fault introduced into excavatability
# faulty_ex_prob is in [0, 1]. For demo, set it to a smaller number such that
# it will has a high chance to see the failure of excavation.
def syn_exca_plan(
        plexil_plan_name,
        runtime_info_filename, xloc_num, dloc_num,
        syn_dir, result_dir, prism_model_filename,
        prism_preprocessor_filename, prism_property_filename,
        max_tried=1, faulty_ex_prob=-1):

    # Create a directory for holding PRISM model, policy file and PLEXIL plan
    # file.
    if not os.path.exists(result_dir):
        try:
            os.mkdir(result_dir)
        except OSError as error:
            print(error)

    cmd = "cp -r ./prism/* " + result_dir
    os.system(cmd)

    # 1 Generate the run-time information: excavation locations and dump locations
    # Based on valid working zone of the arm, generate a pool of valid
    # locations for excavation and dumpping
    print("\n[Step 1]: Synthesize/Load the run-time information.")
    runtime_info_fp_syn = os.path.join(syn_dir, runtime_info_filename)
    if not os.path.exists(runtime_info_fp_syn):
        loc_pool = gen_loc_pool(x_gap=0.2, y_gap=0.1)
        runtime_info_generator = RuntimeInfoExcaGenerator(loc_pool)
        runtime_info_generator.gen_runtime_info(
            xloc_num, dloc_num, runtime_info_fp_syn)

    # When dynamic update of run-time information is enabled, remove it
    runtime_info_fp = os.path.join(result_dir, runtime_info_filename)
    shutil.move(runtime_info_fp_syn, runtime_info_fp)

    # Load runtime information for the following steps
    runtime_info = {}
    with open(runtime_info_fp) as infile:
        runtime_info = json.load(infile)

    print(json.dumps(runtime_info, indent=4, sort_keys=True))

    faults = {}
    if (faulty_ex_prob >= 0) and (faulty_ex_prob <= 1):
        faults["excavation"] = {"ex_prob": faulty_ex_prob}

    # 2 Generate PRISM model
    print("\n[Step 2]: Generate PRISM model")
    # Placeholder: when the runtime information is provided by another program.
    num_xlocs = len(runtime_info['xloc_list'])
    num_dlocs = len(runtime_info['dloc_list'])
    #prism_model_fp = "ow_"+str(num_xlocs)+"ex_"+str(num_dlocs)+"dp.prism"
    prism_generator = PrismGenerator(
        runtime_info, result_dir,
        prism_model_filename, prism_preprocessor_filename)
    prism_generator.generate_prism_model(max_tried)

    # 3 Use PRISM model to extract policy and a plan
    print("\n[Step 3]: Use PRISM model to extract policy and a plan")
    prism_property_fp = os.path.join(result_dir, prism_property_filename)
    prism_model_fp = os.path.join(result_dir, prism_model_filename)
    policy_filename = "policy.adv"
    policy_fp = os.path.join(result_dir, policy_filename)

    cmd_policy_extraction = "prism " + prism_model_fp + \
        " " + prism_property_fp + " -exportadv " + policy_fp
    print("[CMD] " + cmd_policy_extraction)
    p_pe = Popen(cmd_policy_extraction, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p_pe.communicate()

    # Java program, PrismPolicy.class, should be in the same directory level
    # as synplan.py
    cmd_syn_plan = "java PrismPolicy " + policy_fp
    print("[CMD] " + cmd_syn_plan)
    p_sp = Popen(cmd_syn_plan, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p_sp.communicate()
    # prism_syn_plan: [action1, action2, ...]
    prism_syn_plan = stdout.splitlines()[-1]
    print("[prism_syn_plan]: " + str(prism_syn_plan))

    # 4 Plan Translation
    print("\n[Step 4]: Plan Translation")
    plexil_plan_translator = PlexilPlanTranslator()
    scenario_ID = "Excavation"
    #plexil_plan_name = "Exca"
    plexil_plan_dir = result_dir
    plexil_plan_translator.translate(
        scenario_ID,
        runtime_info,
        plexil_plan_name,
        plexil_plan_dir,
        prism_syn_plan,
        faults)

    # For Demo Only. Should be refactored or removed later
    # Update the runtime_info and write to a file for the scenario without a
    # fault
    syn_plan = prism_syn_plan[1:-1].split(', ')
    # Currently only support the case of max_tried=1,
    # which assumes that each action starts with "select_"
    sel_xloc_ID = syn_plan[0][7:]
    xloc_list = runtime_info['xloc_list']
    runtime_info['xloc_list'] = {}
    xloc_list.pop(sel_xloc_ID)
    num_xloc = len(xloc_list)
    xloc_idx = 1
    for key in xloc_list:
        new_key = "xloc" + str(xloc_idx)
        runtime_info['xloc_list'][new_key] = xloc_list[key]
        xloc_idx += 1
    #runtime_info_fp = os.path.join("./", runtime_info_filename)
    with open(runtime_info_fp_syn, "w") as outfile:
        json.dump(runtime_info, outfile)

#########################


def parse_arguments(parser):
    parser.add_argument(
        "--runtime_info_filename",
        type=str,
        required=True,
        help="the path of run-time information")
    parser.add_argument(
        "--result_dir",
        type=str,
        required=True,
        help="the directory for holding all results")
    parser.add_argument(
        "--prism_model_filename",
        type=str,
        required=True,
        help="the name of the prism model")
    parser.add_argument(
        "--prism_property_filename",
        type=str,
        required=True,
        help="the name of the prism property file")
    parser.add_argument(
        "--prism_preprocessor_filename",
        type=str,
        required=True,
        help="the name of the prism preprocessor file")
    parser.add_argument(
        "--xloc_num",
        type=int,
        required=True,
        help="the number of excavation locations")
    parser.add_argument(
        "--dloc_num",
        type=int,
        required=True,
        help="the number of dump locations")
    parser.add_argument(
        "--faulty_ex_prob",
        type=float,
        required=False,
        default=-1,
        help="the changed excavatability by a fault. '-1' means no fault.")
    parser.add_argument(
        "--plexil_plan_name",
        type=str,
        required=True,
        help="the name of the PLEXIL plan to generated.")

    parser.add_argument(
        "--syn_dir",
        type=str,
        required=True,
        help="the root directory of synthesizing plexil plans")

    args = parser.parse_args()

    args_dict = vars(args)

    return args_dict


def main(argv):
    parser = ArgumentParser()
    args_dict = parse_arguments(parser)
    print("Args:")
    print(args_dict)
    print("\n")

    syn_dir = args_dict['syn_dir']
    runtime_info_filename = args_dict['runtime_info_filename']
    xloc_num = args_dict['xloc_num']
    dloc_num = args_dict['dloc_num']
    result_dir = args_dict['result_dir']
    prism_model_filename = args_dict['prism_model_filename']
    prism_preprocessor_filename = args_dict['prism_preprocessor_filename']
    prism_property_filename = args_dict['prism_property_filename']
    faulty_ex_prob = args_dict['faulty_ex_prob']
    plexil_plan_name = args_dict['plexil_plan_name']

    syn_exca_plan(
        plexil_plan_name,
        runtime_info_filename, xloc_num, dloc_num,
        syn_dir, result_dir, prism_model_filename,
        prism_preprocessor_filename, prism_property_filename,
        max_tried=1, faulty_ex_prob=faulty_ex_prob)


if __name__ == "__main__":
    main(sys.argv[1:])
