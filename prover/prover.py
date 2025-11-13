from galois import GF, Poly
from r1cs.r1cs import load_matrices_from_json
from utils.utils import get_coeff_from_poly, lagrange_poly_vector, save_json
from witness.witness import  load_witness_from_json
from py_ecc.bn128.bn128_curve import G1, G2, multiply, curve_order, add
from keys import keys

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

    def generate_proof(self):

        galois_field = GF(curve_order)
        witness = load_witness_from_json(json_path=self.example_path + 'witness.json', galois_field=galois_field)
        L, R, O = load_matrices_from_json(json_path=self.example_path + 'r1cs.json',  galois_field=galois_field)
        srs1, srs2, srs3 = keys.load_proving_key_from_json(json_path=self.example_path + 'proving_key.json')



        # Generate the polynomials of the matrices using Lagrange interpolation
        L_transposed = list(zip(*L))
        R_transposed = list(zip(*R))
        O_transposed = list(zip(*O))


        L_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in L_transposed]
        R_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in R_transposed]
        O_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in O_transposed]
        
        term1 = L_polys[0] * witness[0]
        for i, poly in enumerate(L_polys):
            if i == 0:
                continue
            else:
                term1 += poly * witness[i]

        term2 = R_polys[0] * witness[0]
        for i, poly in enumerate(R_polys):
            if i == 0:
                continue
            else:
                term2 += poly * witness[i]

        term3 = O_polys[0] * witness[0]
        for i, poly in enumerate(O_polys):
            if i == 0:
                continue
            else:
                term3 += poly * witness[i]

        # calculating t(x) and h(x)
        constraints_nb = len(L)
        t_poly = self.define_t_poly(constraints_nb, galois_field=galois_field)
        h_poly = (term1 * term2 - term3) // t_poly

        assert term1 * term2   == term3 + h_poly * t_poly, "QAP relation does not hold: term1 * term2 != term3 + h * t"


        # A_pre_evaluated = [(witness*get_coeff_from_poly(L_polys[i], degree) for i in range(0, len(L[0]))) for degree in range(0, len(L))]
        # B_pre_evaluated = [(witness*get_coeff_from_poly(R_polys[i], degree) for i in range(0, len(R[0]))) for degree in range(0, len(R))]
        # C_pre_evaluated = [(witness*get_coeff_from_poly(O_polys[i], degree) for i in range(0, len(O[0]))) for degree in range(0, len(O))]

        # here we will calculate h(tau)*t(tau)
        h_t_tau = self.evaluate_poly_using_srs(h_poly, srs3)

        # calculating A, B, C
        A = self.evaluate_poly_using_srs(term1, srs1)
        B = self.evaluate_poly_using_srs(term2, srs2)
        C = add(self.evaluate_poly_using_srs(term3, srs1), h_t_tau)

        keys.save_proof_to_json(A, B, C, json_path=self.example_path + 'proof.json')

        return A, B, C

        