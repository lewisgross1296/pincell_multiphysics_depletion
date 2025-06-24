import openmc
import openmc.deplete
import common_input as specs
from mpi4py import MPI
from pathlib import Path
from argparse import ArgumentParser

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


def main(num_procs, continue_run):

    model = openmc.Model.from_model_xml()
    if num_procs > 1:
        openmc.deplete.pool.NUM_PROCESSES = num_procs
    else:
        openmc.deplete.pool.USE_MULTIPROCESSING = False

    # full power values
    pin_power = specs.total_power / (specs.fuel_bundles * specs.pins_per_bundle)
    time_steps = [1, 2, 2, 5, 10, 15, 30, 30]  # short initial steps for BOL jumps
    if rank == 0:
        print(
            f"This simulation will deplete at {pin_power} W with the following time steps (units of days) {time_steps}"
        )
    prev_results = (
        openmc.deplete.Results("depletion_results.h5") if (continue_run) else None
    )
    operator = openmc.deplete.CoupledOperator(
        model, prev_results=prev_results, chain_file="chain_simple.xml"
    )
    integrator = openmc.deplete.CECMIntegrator(
        operator,
        time_steps,
        power=pin_power,
        timestep_units="d",
        continue_timesteps=continue_run,
    )
    integrator.integrate(final_step=True, output=True)


if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument(
        "-np",
        "--n_procs",
        dest="np",
        type=int,
        default=1,
        help="number of processes to deplete with",
    )
    ap.add_argument(
        "-c",
        "--continue",
        dest="continue_run",
        action="store_true",
        help="whether to run depletion as a continue run or not",
    )
    args = ap.parse_args()
    main(args.np, args.continue_run)
