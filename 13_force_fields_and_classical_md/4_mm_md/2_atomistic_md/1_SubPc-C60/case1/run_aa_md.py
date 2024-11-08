#*********************************************************************************
#* Copyright (C) 2016-2021 Alexey V. Akimov
#*
#* This file is distributed under the terms of the GNU General Public License
#* as published by the Free Software Foundation, either version 3 of
#* the License, or (at your option) any later version.
#* See the file LICENSE in the root directory of this distribution
#* or <http://www.gnu.org/licenses/>.
#*
#*********************************************************************************/

###################################################################
# Starting with the file from the test_hamiltonian_mm/test_mm6a.py
#
###################################################################

import sys

if sys.platform=="cygwin":
    from cyglibra_core import *
elif sys.platform=="linux" or sys.platform=="linux2":
    from liblibra_core import *

from libra_py import *


def main():

    #--------------------- Initialization ----------------------

    # Create Universe and populate it
    U = Universe(); LoadPT.Load_PT(U, "elements.txt")

    # Create force field
    uff = ForceField({"bond_functional":"Harmonic",
                      "angle_functional":"Fourier",
                      "dihedral_functional":"General0",
                      "oop_functional":"Fourier",
                      "mb_functional":"LJ_Coulomb","R_vdw_on":10.0,"R_vdw_off":15.0 })
    LoadUFF.Load_UFF(uff,"uff.dat")


    # Create molecular system and initialize the properties
    syst = System()
    LoadMolecule.Load_Molecule(U, syst, "Pc-C60.ent", "pdb")
    syst.determine_functional_groups(0)  # do not assign rings
    syst.init_fragments()
    print("Number of atoms in the system = ", syst.Number_of_atoms)
    atlst1 = list(range(1,syst.Number_of_atoms+1))

    # Creating Hamiltonian and initialize it
    ham = Hamiltonian_Atomistic(1, 3*syst.Number_of_atoms)
    ham.set_Hamiltonian_type("MM")
    ham.set_interactions_for_atoms(syst, atlst1, atlst1, uff, 1, 0)  # 0 - verb, 0 - assign_rings
    ham.show_interactions_statistics()

    # Bind Hamiltonian and the system   
    ham.set_system(syst);   ham.compute();   print("Energy = ", ham.H(0,0), " a.u.")

    # Electronic DOFs
    el = Electronic(1,0)

    # Nuclear DOFs
    mol = Nuclear(3*syst.Number_of_atoms)

    # Initialize MD variables
    nve_md.nve_md_init(syst, mol, el, ham)

    #=================== Propagation ====================
    integrator = "DLML"

    ########################## Cooling #################################

    f = open("_en_cooling.txt","w")
    f.close()

    params = { "dt":20.0, "integrator": "DLML"}

    for i in range(1):
        syst.set_atomic_q(mol.q)
        syst.print_xyz("_mol_cooling.xyz",i)

        for j in range(1):
            ekin, epot, etot = nve_md.nve_md_step(syst, mol, el, ham, params)

        syst.cool()

        f = open("_en_cooling.txt","a")
        f.write("i= %3i ekin= %8.5f  epot= %8.5f  etot= %8.5f\n" % (i, ekin, epot, etot))
        f.close()


    ########################## Production MD #################################

    rnd = Random()

    syst.init_atom_velocities(300.0, rnd)

    f = open("_en_md.txt","w")
    f.close()

    params["dt"] = 40.0

    for i in range(1000):
        syst.set_atomic_q(mol.q)
        syst.print_xyz("_mol_md.xyz",i)

        for j in range(10):
            ekin, epot, etot = nve_md.nve_md_step(syst, mol, el, ham, params)

        f = open("_en_md.txt","a")
        f.write("i= %3i ekin= %8.5f  epot= %8.5f  etot= %8.5f\n" % (i, ekin, epot, etot))
        f.close()


main()

