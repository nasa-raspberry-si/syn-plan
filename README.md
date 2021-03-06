# syn-plan

## Code Organization
   * gen_runtime_info_exca.py: Synthesize the run-time information for planning excavation.
   * gen_prism_model.py: Generate the fixed part of a PRISM model using PRISM preprocessor and then dynamically add up non-fixed part (e.g., rewards) based on run-time information.
   * plexil_plan_translator.py: Translate a PRISM plan to a PLEXIL plan using a set of primitive actions, each of which is a PLEXIL plan.
   * run.py: Example script for generating a PLEXIL plan when the numbers of excavation locations and dump locations are given. (Check the usage below.)
   * PrismPolicy.java: Java program for extracting actions from a Prism policy. It is suggested to compile it locally before using it.

## Usage
### Command To Run
`python run.py --syn_dir ./ --plexil_plan_name Exca --runtime_info_filename rt_info.json --xloc_num 8 --dloc_num 6 --result_dir planning_exca_result --prism_model_filename ow_planner.prism --prism_preprocessor_filename autonomy-excavate.pp --prism_property_filename excavate.props --always_new_runtime_info True --faulty_ex_prob 0.1`

The faulty_ex_prob with a value of 0.1 indicates that actual excavatability, the probability of successful excavation, will change to original_excavatability*0.1.

### Result
Inside the resulting directory, **planning_exca_result**, there are
   * Synthesized run-time information for the excavation scenarion in **rt_info.json**.
   * Automatically generated PRISM model, **ow_planner.prism**.
   * Extracted Prism policy in **policy.adv**.
   * The PLEXIL plan **Exca.plp** translated from the Prism policy above.

