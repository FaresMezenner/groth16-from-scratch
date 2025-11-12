from utils.utils import  hadamard_product, linear_pairing_vectors, matrix_vector_product, matrix_vector_product_ecc, pair_vector_with_G1, pair_vector_with_G2, vectors_modular_equal
from witness.witness import load_somewhat_zk_proof_witness_from_json, load_witness_from_json
from r1cs.r1cs import load_matrices_from_json
from py_ecc.bn128.bn128_curve import G1, G2

class Verifier:
    def __init__(self, modulo = 101, example_path='./examples/example1/'):
        self.modulo = modulo
        self.example_path = example_path



    def verify_proof_r1cs_no_zk(self):
        a = load_witness_from_json(json_path=self.example_path + 'witness.json', modulo=self.modulo)
        L, R, O = load_matrices_from_json(json_path=self.example_path + 'r1cs.json', modulo=self.modulo)
        # sanity checks for matrices are already done in loading functions
        # check that the number of columns in L, R, O matches the length of witness a
        num_vars = len(a)
        assert all(len(row) == num_vars for row in L), "All rows in the matrices L, R, and O, must have the same number of columns as witness length"
        
        # first we compute L*a, R*a, O*a
        L_a = matrix_vector_product(L, a, self.modulo)
        R_a = matrix_vector_product(R, a, self.modulo)
        O_a = matrix_vector_product(O, a, self.modulo)


        # now we calculate the Hadamard product (L*a) ⊙ (R*a)
        hadamard_product_L_R = hadamard_product(L_a, R_a, self.modulo)

        # finally we check if O*a == (L*a) ⊙ (R*a)
        assert vectors_modular_equal(O_a, hadamard_product_L_R, self.modulo), "R1CS verification failed: O*a does not equal (L*a) ⊙ (R*a)" 
        
        print("R1CS verification succeeded.")
        return True
    
    def verify_somewhat_zk_proof(self):
        witness_g1, witness_g2 = load_somewhat_zk_proof_witness_from_json(json_path=self.example_path + 'somewhat_zk_proof_witness.json')
        # verifying that they encrypt the same witness
        witness_g1_paired = pair_vector_with_G2(witness_g1)
        witness_g2_paired = pair_vector_with_G1(witness_g2)
        assert witness_g1_paired == witness_g2_paired, "Somewhat ZK proof verification failed: Encrypted witnesses do not match"

        # calculate L_w_g1, R_w_g2, O_w
        L, R, O = load_matrices_from_json(json_path=self.example_path + 'r1cs.json')
        L_w_g1 = matrix_vector_product_ecc(L, witness_g1)
        R_w_g2 = matrix_vector_product_ecc(R, witness_g2)
        O_w_g1 = matrix_vector_product_ecc(O, witness_g1)
        O_w = pair_vector_with_G2(O_w_g1)
        # we could also calculate O_w directly like this:
        # O_w = matrix_vector_product_ecc(O, witness_g1_paired)

        # calculate pairings
        pairing_L_R = linear_pairing_vectors(L_w_g1, R_w_g2)
        # verify that O_w == pairing_L_R
        assert O_w == pairing_L_R, "Somewhat ZK proof verification failed: O_w does not equal pairing(L_w_g1, R_w_g2)"

        print("Somewhat ZK proof verification succeeded.")
        return True

