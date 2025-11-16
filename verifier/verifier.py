
from py_ecc.bn128.bn128_curve import G2, curve_order, multiply, add
from py_ecc.bn128.bn128_pairing import pairing
from keys import keys
from witness import witness
from galois import GF

class Verifier:
    def __init__(self, example_path='./examples/example1/'):

        self.example_path = example_path
    
    def calulate_x(self, psi ):
        public_witness = witness.load_public_witness_from_json(
            json_path=self.example_path + 'public_witness.json',
            galois_field=GF(curve_order)
        )
        X = None
        for i in range(len(public_witness)):
            a_i = public_witness[i]
            psi_i = psi[i]
            term = multiply(psi_i, int(a_i))
            X = term if X is None else add(X, term)
        return X

    def verify(self):
        A, B, C = keys.load_proof_from_json(json_path=self.example_path + 'proof.json')
        alpha, beta, delta, gamma, psi = keys.load_verifying_key_from_json(json_path=self.example_path + 'verifying_key.json')

        X = self.calulate_x(psi)
        
        assert pairing(B, A) == pairing(beta, alpha) * pairing(gamma, X) * pairing(delta, C), "Proof verification failed."

        print("Proof verification succeeded.")
        return True