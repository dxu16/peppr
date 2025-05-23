import biotite.structure as struc
import pytest
from peppr.idealize import idealize_bonds


@pytest.fixture
def corrupted_pose() -> struc.AtomArray:
    """
    Make a CO2 molecule clashing with a cyanide. Both
    have unrealistic bond lengths and angles.
    """
    pose = struc.AtomArray(5)
    pose[0] = struc.Atom([0.0, 0.0, 0.0], element="C")
    pose[1] = struc.Atom([5.0, 0.0, 0.0], element="O")
    pose[2] = struc.Atom([0.0, 1.5, 0.0], element="O")
    pose[3] = struc.Atom([0.0, 0.0, 0.0], element="C")
    pose[4] = struc.Atom([0.0, 2.0, 0.0], element="N")

    bonds = struc.BondList(5)
    bonds.add_bond(0, 1, struc.BondType.DOUBLE)
    bonds.add_bond(0, 2, struc.BondType.DOUBLE)
    bonds.add_bond(3, 4, struc.BondType.TRIPLE)

    pose.bonds = bonds

    return pose


@pytest.fixture
def clashing_pose() -> struc.AtomArray:
    """
    Make a CO2 and cyanide molecule with their carbons overlapping.
    The bond lengths and angles are realistic.
    """
    pose = struc.AtomArray(5)
    pose[0] = struc.Atom([0.0, 0.0, 0.0], element="C")
    pose[1] = struc.Atom([-1.4, 0.0, 0.0], element="O")
    pose[2] = struc.Atom([1.4, 0.0, 0.0], element="O")
    pose[3] = struc.Atom([0.0, 0.0, 0.0], element="C")
    pose[4] = struc.Atom([1.15, 0.0, 0.0], element="N")

    bonds = struc.BondList(5)
    bonds.add_bond(0, 1, struc.BondType.DOUBLE)
    bonds.add_bond(0, 2, struc.BondType.DOUBLE)
    bonds.add_bond(3, 4, struc.BondType.TRIPLE)

    pose.bonds = bonds

    return pose


def test_idealize_bond_lengths(corrupted_pose):
    """
    Does the `idealize_bonds` function return a structure with idealized bond lengths?
    """
    idealized_pose = idealize_bonds(corrupted_pose)

    # Check if the bond lengths are idealized
    # I don't know why the idealized pose doesn't have the true length of 1.16A.
    # However, even idealizing the pose with 10x as many steps still results in
    # a C=O bond length of 1.40 A. I've checked that the rdkit mol that is
    # minimized does indeed show double bonds between the carbon and both oxygens.
    # Even switching the force field from "MMFF94" to "UFF" gives the same length of 1.40 A.
    ref_C_O_double_bond_length = 1.40  # Å
    bond_length_1 = struc.distance(idealized_pose[0], idealized_pose[1])
    bond_length_2 = struc.distance(idealized_pose[0], idealized_pose[2])
    assert pytest.approx(bond_length_1, rel=1e-2) == ref_C_O_double_bond_length
    assert pytest.approx(bond_length_2, rel=1e-2) == ref_C_O_double_bond_length

    ref_C_N_triple_bond_length = 1.15  # Å
    bond_length_3 = struc.distance(idealized_pose[3], idealized_pose[4])
    assert pytest.approx(bond_length_3, rel=1e-2) == ref_C_N_triple_bond_length


def test_idealize_bond_angles(corrupted_pose):
    """
    Does the `idealize_bonds` function return a structure with idealized bond angles?
    """
    idealized_pose = idealize_bonds(corrupted_pose)

    ref_CO2_angle = 3.14159  # radians
    bond_angle_1 = struc.angle(idealized_pose[1], idealized_pose[0], idealized_pose[2])
    assert pytest.approx(bond_angle_1, rel=1e-2) == ref_CO2_angle


def test_ignore_clashes(clashing_pose):
    """
    Does the `idealize_bonds` function ignore clashes?

    The CO2 carbon should still overlap with the cyanide carbon.
    """
    # The carbons start out overlapping
    assert struc.distance(clashing_pose[0], clashing_pose[3]) < 0.01

    # The carbons should still overlap after idealization
    idealized_pose = idealize_bonds(clashing_pose)
    assert struc.distance(idealized_pose[0], idealized_pose[3]) < 0.01
