#!/bin/bash

plexil_plan_name=$1
fault_ex_prob=$2

xloc_num=8
dloc_num=6


ws_root="/home/jsu/Projects/oceanwaters_ws"

plan_dir="${ws_root}/src/ow_autonomy/src/plans"
dev_plan_dir="${ws_root}/devel/etc/plexil"

cur_dir=$(pwd)

syn_dir="${ws_root}/src/ow_autonomy/syn-plan"

#result_dir="${syn_dir}/planning_exca_result"
result_dir="${syn_dir}/${plexil_plan_name}"

#plexil_plan_name="Exca"
plexil_plan_plp="${plexil_plan_name}.plp"
plexil_plan_plx="${plexil_plan_name}.plx"

cd ${syn_dir}
python run.py --syn_dir "${syn_dir}" --plexil_plan_name "${plexil_plan_name}" --runtime_info_filename rt_info.json --xloc_num "${xloc_num}" --dloc_num "${dloc_num}" --result_dir "${result_dir}" --prism_model_filename ow_planner.prism --prism_preprocessor_filename autonomy-excavate.pp --prism_property_filename excavate.props --faulty_ex_prob ${fault_ex_prob}

# copy syntheized PLEXIL plan into ../src/plans for compilation
cd "${result_dir}"
cp "${plexil_plan_plp}" "${plan_dir}"
cd "${plan_dir}"
plexilc "${plexil_plan_plp}"
cp "${plexil_plan_plx}" "${dev_plan_dir}"
#ln -s "${plexil_plan_plx}" "${dev_plan_dir}"/"${plexil_plan_plx}"



cd ${cur_dir}




