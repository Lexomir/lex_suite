import bpy
from ..utils import *
from collections import OrderedDict
from enum import Enum

class InputType(Enum):
    FLOAT = 0
    VEC2 = 1
    VEC3 = 2
    VEC4 = 3
    NORMAL = 4

def serialize_input_type(input_type):
    if input_type == InputType.FLOAT: return "float"
    elif input_type == InputType.VEC2: return "float2"
    elif input_type == InputType.VEC3: return "float3"
    elif input_type == InputType.VEC4: return "float4"
    elif input_type == InputType.NORMAL: return "float3"


def export_shader(material, shader_node, filepath):
    shader_template_filepath = os.path.abspath(os.path.dirname(__file__) + "/templates/unity_shader_template.shader")
    with open(shader_template_filepath, "r") as template_file:
        shader_output = template_file.read()

    parameters = {'textures':{}, 'colors':{}, 'floats':{}}
    input_variables = {}
    dependencies = OrderedDict()
    collected_data = {'parameters':parameters, 'input_variables':input_variables, 'dependencies':dependencies}

    # get the values for the pbr output (while collecting parameter data, etc)
    albedo_exp = find_input_or_default_expression(input=shader_node.inputs['Base Color'], input_type=InputType.VEC4, collected_data=collected_data)
    normal_exp = find_input_or_default_expression(input=shader_node.inputs['Normal'], input_type=InputType.NORMAL, collected_data=collected_data)

    # generate input variables
    serialized_input_variable_declarations = "\n".join(["{} {};".format(var_type, var_name) for var_name, var_type in input_variables.items()])

    # serialize parameter lists
    serialized_tex_parameter_list = "\n".join(['{} ("{}", 2D) = "white" {{}}'.format(name, details['label']) for name, details in parameters['textures'].items()])
    serialized_color_parameter_list = "\n".join(['{} ("{}", Color) = ({},{},{},{})'.format(
        name, name, round(details['default'][0], 5), round(details['default'][1], 5), round(details['default'][2], 5), round(details['default'][3], 5)) for name, details in parameters['colors'].items()])
    serialized_float_parameter_list = "\n".join(['{} ("{}", Float) = {}'.format(name, name, round(details['default'], 5)) for name, details in parameters['floats'].items()])
    
    # serialize parameter variable declarations
    serialized_tex_param_var_declarations = "\n".join(['sampler2D {};'.format(name) for name in parameters['textures']])
    serialized_color_param_var_declarations = "\n".join(['fixed4 {};'.format(name) for name in parameters['colors']])
    serialized_float_param_var_declarations = "\n".join(['float {};'.format(name) for name in parameters['floats']])

    # serialized dependencies
    serialized_dependencies = "\n".join([assign_statement for node_name, assign_statement in dependencies.items()])

    shader_output = shader_output.replace("{ShaderName}", make_valid_name(material.name))
    shader_output = shader_output.replace("{ParameterList}", "\n".join([serialized_tex_parameter_list, serialized_color_parameter_list, serialized_float_param_var_declarations]))
    shader_output = shader_output.replace("{InputVariableDeclarations}", serialized_input_variable_declarations)
    shader_output = shader_output.replace("{ParameterVariableDeclarations}", 
        "\n".join([serialized_tex_param_var_declarations, serialized_color_param_var_declarations, serialized_float_param_var_declarations]))
    
    shader_output = shader_output.replace("{Dependencies}", serialized_dependencies)
    shader_output = shader_output.replace("{Albedo}", albedo_exp)
    shader_output = shader_output.replace("{Normal}", normal_exp)

    with open(filepath, "w") as output_file:
        output_file.write(shader_output)
        

# generates an expression for the input 
# uses 'find_expression_and_dependencies' if the input is a node, otherwise returns a default expression
def find_input_or_default_expression(input, input_type, collected_data):
    if len(input.links) == 1:  # create an assignment statement as a dependency and return the new variable as the 'expression'
        input_node = input.links[0].from_node
        input_name = "{}_{}".format(make_valid_name(input.links[0].to_node.name), make_valid_name(input_node.name))
        if input_node.name not in collected_data['dependencies']:
            input_exp = find_expression_and_dependencies(node=input_node, expected_type=input_type, collected_data=collected_data)
            input_assignment = "{} {} = {};".format(serialize_input_type(input_type), input_name, input_exp)
            collected_data['dependencies'][input_node.name] = input_assignment
        input_exp = input_name
        return input_exp
    else:    # return a default expression
        if input_type == InputType.NORMAL:
            return "float3(.5, .5, 1)"
        elif input_type == InputType.VEC2:
            return "float2({}, {})".format(round(input.default_value[0], 5), round(input.default_value[1], 5))
        elif input_type == InputType.VEC3:
            return "float3({}, {}, {})".format(round(input.default_value[0], 5), round(input.default_value[1], 5), round(input.default_value[2], 5))
        elif input_type == InputType.VEC4:
            return "float4({}, {}, {}, {})".format(round(input.default_value[0], 5), round(input.default_value[1], 5), round(input.default_value[2], 5), round(input.default_value[3], 5))
        elif input_type == InputType.FLOAT:
            return "{}".format(round(input.default_value, 5))
        else:
            raise "Unsupported input type {}".format(input_type)


# creates an expression for a node (will recurse in order generate dependent code for the expression)
def find_expression_and_dependencies(node, expected_type, collected_data):
    if node.type == "TEX_IMAGE":
        texture_variable = make_valid_name(node.name)
        texture_label = node.label
        uv_input_variable = "uv{}".format(texture_variable)
        collected_data['parameters']['textures'][texture_variable] = {'label':texture_label, 'default': node.image.filepath}  # store this as a parameter
        collected_data['input_variables'][uv_input_variable] = "float2"  # store this as an input variable
        return "tex2D({}, {})".format(texture_variable, uv_input_variable)
    elif node.type == "RGB":
        color_variable = make_valid_name(node.name)
        color_label = node.label
        color = node.outputs[0].default_value
        collected_data['parameters']['colors'][color_variable] = {'label':color_label, 'default':color}  # store this as a parameter
        return "{}.rgba".format(color_variable)
    elif node.type == "VALUE":
        val_variable = make_valid_name(node.name)
        val_label = node.label
        val = node.outputs[0].default_value
        collected_data['parameters']['floats'][val_variable] = {'label':val_label, 'default':val}  # store this as a parameter
        return "{}".format(val_variable)
    elif node.type == "NORMAL_MAP":
        expression = find_input_or_default_expression(input=node.inputs['Color'], input_type=InputType.NORMAL, collected_data=collected_data)
        return expression
    elif node.type == "MATH":
        input0_exp = find_input_or_default_expression(input=node.inputs[0], input_type=InputType.FLOAT, collected_data=collected_data)
        input1_exp = find_input_or_default_expression(input=node.inputs[1], input_type=InputType.FLOAT, collected_data=collected_data)

        if node.operation == "ADD":
            return "{} + {}".format(input0_exp, input1_exp)
        elif node.operation == "SUBTRACT":
            return "{} - {}".format(input0_exp, input1_exp)
        elif node.operation == "MULTIPLY":
            return "{} * {}".format(input0_exp, input1_exp)
        elif node.operation == "DIVIDE":
            return "{} / {}".format(input0_exp, input1_exp)
        elif node.operation == "SINE":
            return "sin({})".format(input0_exp)
        elif node.operation == "COSINE":
            return "cos({})".format(input0_exp)
        else:
            raise "Unsupported Node Math Operation {}".format(node.operation)



def get_input(node, index):
    if index < len(node.inputs) and len(node.inputs[index].links) == 1:
        return node.inputs[index].links[0].from_node
    else:
        return None
