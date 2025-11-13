from galois import GF
from r1cs.r1cs import load_matrices_from_json
from utils.utils import lagrange_poly_vector, save_json
from witness.witness import  load_witness_from_json, save_somewhat_zk_proof_witness_to_json
from py_ecc.bn128.bn128_curve import G1, G2, multiply, curve_order
import random

class Prover:
    def __init__(self, example_path = './examples/example1/'):
        self.example_path = example_path
    

    def generate_somewhate_zk_proof_r1cs(self):
        witness = load_witness_from_json(json_path=self.example_path + 'witness.json')

        wintess_G1 = [multiply(G1, w) for w in witness ]
        wintess_G2 = [multiply(G2, w) for w in witness ]




        save_somewhat_zk_proof_witness_to_json(wintess_G1, wintess_G2, json_path=self.example_path + 'somewhat_zk_proof_witness.json')

        return wintess_G1, wintess_G2
    
    def generate_qap_proof(self):

        witness = load_witness_from_json(json_path=self.example_path + 'witness.json', modulo=curve_order)
        L, R, O = load_matrices_from_json(json_path=self.example_path + 'r1cs.json', modulo=curve_order)

        galois_field = GF(curve_order)


        # Generate the polynomials of the matrices using Lagrange interpolation
        L_transposed = list(zip(*L))
        R_transposed = list(zip(*R))
        O_transposed = list(zip(*O))


        L_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in L_transposed]
        R_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in R_transposed]
        O_polys = [lagrange_poly_vector(col, galois_field=galois_field) for col in O_transposed]

        # Evaluate the polynomials at a random point tau
        tau = galois_field(random.randint(0, curve_order ))
        L_evaluated = [poly(tau, field=galois_field)   for poly in L_polys]
        R_evaluated = [poly(tau, field=galois_field)   for poly in R_polys]
        O_evaluated = [poly(tau, field=galois_field)   for poly in O_polys]

        # Compute the proof elements
        u =galois_field(0)
        for w, l in zip(witness, L_evaluated):
            u += w * l
        v =galois_field(0)
        for w, r in zip(witness, R_evaluated):
            v += w * r
        w =galois_field(0)
        for w_, o in zip(witness, O_evaluated):
            w += w_ * o
        
        # # let's define the target polynomial t(x) = (x-1)(x-2)...(x-n) where n is the number of constraints evaluated at tau
        t = galois_field(1)
        for i in range(1, len(L)+1):
            t = t * (tau - galois_field(i))



        # # let's calculate h(x) now evaluated at tau
        h = (u*v - w)  // t


        assert u*v == w + h*t , "QAP relation does not hold: u*v != w + h*t"

        #  define A, B, and C
        A = multiply(G1, int(u))
        B = multiply(G2, int(v))
        C = multiply(G1, int(w + h*t))

        print("QAP proof generation succeeded.")
        print(f"QAP elements:\nA: {A}\nB: {B}\nC: {C}")



        return A, B, C

        