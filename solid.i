!include common_input.i 

[Mesh]
  [file]
    type = FileMeshGenerator
    file = mesh_in.e
  []
[]

[Variables]
  [temp]
    initial_condition = ${initial_T}
  []
[]

[AuxVariables]
  [heat_source]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[Kernels]
  [hc]
    type = HeatConduction
    variable = temp
  []
  [heat]
    type = CoupledForce
    variable = temp
    v = heat_source
  []
[]

[Functions]
  [T_fluid]
    type = ParsedFunction
    expression = '573.0 + 50.0 * (z / 300.0)'
    # TODO change to below when verified that this is not the problem
    # expression = 'inlet_T + dT * (z / L)'
    # symbol_names = 'inlet_T dT L'
    # symbol_values = '${inlet_T} ${dT} ${L}'
  []
[]

[BCs]
  [surface]
    type = ConvectiveFluxFunction
    T_infinity = T_fluid

    coefficient = '0.1' # W/cm2-K
    variable = temp
    boundary = 'rmax_c'
  []
[]

[ThermalContact]
  # This adds boundary conditions bewteen the fuel and the cladding, which represents
  # the heat flux in both directions as
  # q''= h * (T_1 - T_2)
  # where h is a conductance that accounts for conduction through a material and
  # radiation between two infinite parallel plate gray bodies.
  [one_to_two]
    type = GapHeatTransfer
    variable = temp
    primary = 'rmax'
    secondary = 'rmin_c'

    # we will use a quadrature-based approach to find the gap width and cross-side temperature
    quadrature = true

    # emissivity of the fuel
    emissivity_primary = 0.8

    # emissivity of the clad
    emissivity_secondary = 0.8

    # thermal conductivity of the gap material
    gap_conductivity = 1.0

    # geometric terms related to the gap
    gap_geometry_type = CYLINDER
    cylinder_axis_point_1 = '0 0 0'
    cylinder_axis_point_2 = '0 0 ${L}'
  []
[]

[Materials]
  [k_clad]
    type = GenericConstantMaterial
    prop_values = '0.5' # W/cm-K
    prop_names = 'thermal_conductivity'
    block = '1'
  []
  [k_fuel]
    type = GenericConstantMaterial
    prop_values = '0.05'  # W/cm-K
    prop_names = 'thermal_conductivity'
    block = '2 3'
  []
[]

[Executioner]
  type = Transient
  nl_abs_tol = 1e-8
  num_steps = 5
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  exodus = true
  print_linear_residuals = false
[]

[MultiApps]
  [openmc]
    type = TransientMultiApp
    input_files = 'openmc.i'
    execute_on = timestep_end
  []
[]

[Transfers]
  [heat_source_from_openmc]
    type = MultiAppGeneralFieldShapeEvaluationTransfer
    from_multi_app = openmc
    variable = heat_source
    source_variable = heat_source
    from_postprocessors_to_be_preserved = heat_source
    to_postprocessors_to_be_preserved = source_integral
  []
  [temp_to_openmc]
    type = MultiAppGeneralFieldShapeEvaluationTransfer
    to_multi_app = openmc
    variable = temp
    source_variable = temp
  []
[]

[Postprocessors]
  [source_integral]
    type = ElementIntegralVariablePostprocessor
    variable = heat_source
    execute_on = transfer
  []
  [max_T]
    type = NodalExtremeValue
    variable = temp
  []
[]
