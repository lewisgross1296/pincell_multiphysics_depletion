import openmc
import common_input as specs


def build_model():
    model =  openmc.Model()

    # input materials
    uo2 = openmc.Material(name='UO2 fuel at 2.4% wt enrichment')
    uo2.set_density('g/cm3', 10.29769)
    uo2.add_element('U', 1., enrichment=2.4)
    uo2.add_element('O', 2.)

    helium = openmc.Material(name='Helium for gap')
    helium.set_density('g/cm3', 0.001598)
    helium.add_element('He', 2.4044e-4)

    zircaloy = openmc.Material(name='Zircaloy 4')
    zircaloy.set_density('g/cm3', 6.55)
    zircaloy.add_element('Sn', 0.014  , 'wo')
    zircaloy.add_element('Fe', 0.00165, 'wo')
    zircaloy.add_element('Cr', 0.001  , 'wo')
    zircaloy.add_element('Zr', 0.98335, 'wo')

    borated_water = openmc.Material(name='Borated water')
    borated_water.set_density('g/cm3', 0.740582)
    borated_water.add_element('B', 4.0e-5)
    borated_water.add_element('H', 5.0e-2)
    borated_water.add_element('O', 2.4e-2)
    borated_water.add_s_alpha_beta('c_H_in_H2O')

    # build geometry
    # create cylindrical surfaces
    fuel_or = openmc.ZCylinder(r=specs.r_fuel, name='Fuel OR')
    clad_ir = openmc.ZCylinder(r=specs.ri_clad, name='Clad IR')
    clad_or = openmc.ZCylinder(r=specs.ro_clad , name='Clad OR')

    # cells for each region
    fuel_cell = openmc.Cell(region = -fuel_or, fill = uo2, name="fuel")
    gap_cell = openmc.Cell(region = +fuel_or & -clad_ir, fill = helium, name = "gap")
    clad_cell = openmc.cell(region = +clad_ir & -clad_or, fill = zircaloy, name= "clad")
    pin_universe = openmc.Universe(cells=[fuel_cell,gap_cell,clad_cell])

    # Create a region represented as the inside of a rectangular prism
    dz = specs.dz
    min = 0.0 # cm
    max = 10*dz # cm

    z_min = openmc.ZPlane(z0=min, boundary_type = "vacuum")
    z_max = openmc.ZPlane(z0=max, boundary_type = "vacuum")

    pin_bbox = openmc.model.RectangularPrism(specs.pitch, specs.pitch, boundary_type='reflective') # bounding box for pincell


    lattice = openmc.RectLattice()
    lattice.lower_left = (-specs.pitch/2, -specs.pitch/2, min)
    lattice.specs.pitch = (specs.pitch, dz)
    lattice.outer = openmc.Universe(cells=(openmc.Cell(fill=borated_water,)))
    lattice.universes = [pin_universe]

    model_cell = openmc.Cell(fill = lattice, region=-pin_bbox & +z_min & -z_max)
    model.geometry = openmc.Geometry(cells=[model_cell])

    # export materials from geometry
    mats_from_geom = list(model.geometry.get_all_materials().values())
    model.materials = mats_from_geom

    # build settings
    settings = openmc.Settings()
    settings = openmc.Settings()
    settings.batches = 1500
    settings.inactive = 500
    settings.particles = 20000

    # Create an initial uniform spatial source distribution over fissionable zones
    lower_left = (-specs.pitch/2, -specs.pitch/2, min)
    upper_right = (specs.pitch/2, specs.pitch/2, max)
    uniform_dist = openmc.stats.Box(lower_left, upper_right, only_fissionable=True)
    settings.source = openmc.IndependentSource(space=uniform_dist)

    model.settings = settings


    return model

def main():
    model = build_model()
    model.export_to_model_xml()

if __name__ == "__main__":