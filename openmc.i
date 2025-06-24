!include common_input.i

[Mesh]
  [file]
    type = FileMeshGenerator
    file = mesh_in.e
  []
[]

[AuxVariables]
  [cell_temperature]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[AuxKernels]
  [cell_temperature]
    type = CellTemperatureAux
    variable = cell_temperature
  []
[]

[Problem]
  type = OpenMCCellAverageProblem
  verbose = true
  power = ${fparse total_power / (fuel_bundles * pins_per_bundle)}
  temperature_blocks = '1 2 3'
  cell_level = 1
  volume_calculation = vol

  [Tallies]
    [heat_source]
      type = CellTally
      block = '2 3'
      name = heat_source
    []
  []
[]

[UserObjects]
  [vol]
    type = OpenMCVolumeCalculation
    n_samples = 100000
  []
[]

[Executioner]
  type = Transient
[]

[Outputs]
  exodus = true
  csv = true
[]

[Postprocessors]
  [heat_source]
    type = ElementIntegralVariablePostprocessor
    variable = heat_source
  []
  [max_tally_rel_err]
    type = TallyRelativeError
  []
  [max_heat_source]
    type = ElementExtremeValue
    variable = heat_source
  []
[]
