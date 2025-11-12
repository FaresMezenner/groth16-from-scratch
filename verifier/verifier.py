from utils.utils import  hadamard_product, matrix_vector_product, vectors_modular_equal
from witness.witness import load_witness_from_json
from r1cs.r1cs import load_matrices_from_json


class VerifierNoZK:
    def __init__(self, modulo, example_path='./examples/example1/'):
        self.modulo = modulo
        self.example_path = example_path



    def verify_proof_r1cs_no_zk(self):
        a = load_witness_from_json(json_path=self.example_path + 'witness.json')
        L, R, O = load_matrices_from_json(json_path=self.example_path + 'r1cs.json')
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
                
        return True