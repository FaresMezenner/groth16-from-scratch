from galois import GF, Poly
from r1cs.r1cs import load_matrices_from_json
from utils.utils import get_coeff_from_poly, lagrange_poly_vector, save_json
from witness.witness import  load_witness_from_json, public_inputs_length
from py_ecc.bn128.bn128_curve import G1, G2, multiply, curve_order, add
from py_ecc.bn128.bn128_pairing import pairing
from keys import keys
import random

class Prover:
    def __init__(self, example_path = './examples/example1/'):
        self.example_path = example_path
    
    def define_t_poly(self, constraints_nb, galois_field=GF(curve_order)):
        # t(x) = (x-1)(x-2)...(x - constraints_nb)
        t = Poly([1], field=galois_field)  # start with polynomial "1"
        for i in range(1, constraints_nb + 1):
            t *= Poly([1, -i], field=galois_field)  # multiply by (x - i)
        return t
    
    def evaluate_poly_using_srs(self, poly, srs):
        result = None
        for degree in range(0, poly.degree + 1):
            coeff = get_coeff_from_poly(poly, degree)
            srs_point = srs[degree]
            term = multiply(srs_point, int(coeff))
            result = term if result is None else add(result, term)
        return result
    
    def evaluate_problematic_C_part(self, witness, psi):
        num_public_inputs = public_inputs_length(json_path=self.example_path + 'public_witness.json')
        problematic_C_part = None
        for i in range(len(witness) - num_public_inputs):
            a_i = witness[i + num_public_inputs]
            psi_i = psi[i]
            term = multiply(psi_i, int(a_i))
            problematic_C_part = term if problematic_C_part is None else add(problematic_C_part, term)
        return problematic_C_part
    
    def calculate_poly_sum_with_witness(self, polys, witness):
        result_poly = polys[0] * witness[0]
        for i, poly in enumerate(polys):
            if i == 0:
                continue
            else:
                result_poly += poly * witness[i]
        return result_poly
    
    #sanity check for srs that is encrypted in G1
    def sanity_check_srs_G1(self, srs, encrypted_tau):
        for i in range(0, len(srs)-1):
            left = pairing(encrypted_tau, srs[i] )
            right = pairing(G2, srs[i+1])
            assert left == right, f"SRS G1 sanity check failed at index {i}"
    
    #sanity check for srs that is encrypted in G2
    def sanity_check_srs_G2(self, srs, encrypted_tau):
        for i in range(0, len(srs)-1):
            left = pairing(srs[i], encrypted_tau )
            right = pairing(srs[i+1], G1)
            assert left == right, f"SRS G2 sanity check failed at index {i}"



    def generate_proof(self):

        galois_field = GF(curve_order)
        witness = load_witness_from_json(json_path=self.example_path + 'witness.json', galois_field=galois_field)
        L, R, O = load_matrices_from_json(json_path=self.example_path + 'r1cs.json',  galois_field=galois_field)
        srs1, srs2, srs3, psi, alpha, beta_G1, beta_G2, delta_G1, delta_G2 = keys.load_proving_key_from_json(json_path=self.example_path + 'proving_key.json')

        # sanity check for srs1 and srs2
        self.sanity_check_srs_G1(srs1, srs2[1])  # encrypted tau in G2 is srs2[1]
        self.sanity_check_srs_G2(srs2, srs1[1]) # encrypted tau in G1 is srs1[1]

        # Generate the polynomials of the matrices using Lagrange interpolation
        L_transposed = list(zip(*L))
        R_transposed = list(zip(*R))
        O_transposed = list(zip(*O))


        L_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in L_transposed]
        R_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in R_transposed]
        O_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in O_transposed]
        
        u_x = self.calculate_poly_sum_with_witness( L_polys, witness)

        v_x = self.calculate_poly_sum_with_witness( R_polys, witness)

        w_x = self.calculate_poly_sum_with_witness( O_polys, witness)

        # calculating t(x) and h(x)
        constraints_nb = len(L)
        t_poly = self.define_t_poly(constraints_nb, galois_field=galois_field)
        h_poly = (u_x * v_x - w_x) // t_poly

        assert u_x * v_x   == w_x + h_poly * t_poly, "QAP relation does not hold: term1 * term2 != term3 + h * t"

        # here we will calculate h(tau)*t(tau)
        h_t_tau = self.evaluate_poly_using_srs(h_poly, srs3)

        # and here, we will calculate the problematic part of C (\alpha \sum_{i=1}^{m} a_i v_i(\tau) + \beta \sum_{i=1}^{m} a_i u_i(\tau) + \sum_{i=1}^{m} a_i w_i(\tau))
        problematic_C_part = self.evaluate_problematic_C_part(witness, psi)

        # calculating A, B, C using salting
        r = random.randint(1, curve_order )
        s = random.randint(1, curve_order )
        A_1 = add(add(self.evaluate_poly_using_srs(u_x, srs1), alpha), multiply(delta_G1, r))
        
        B_1 = add(add(self.evaluate_poly_using_srs(v_x, srs1), beta_G1) , multiply(delta_G1, s))
        B_2 = add(add(self.evaluate_poly_using_srs(v_x, srs2), beta_G2), multiply(delta_G2, s))
        C_1 = add(add(add(add(problematic_C_part, h_t_tau), multiply(A_1, s)), multiply(B_1, r)), multiply(delta_G1, (-r * s)%curve_order))

        keys.save_proof_to_json(A_1,  B_2, C_1, json_path=self.example_path + 'proof.json')


        

        return A_1, B_2, C_1

        