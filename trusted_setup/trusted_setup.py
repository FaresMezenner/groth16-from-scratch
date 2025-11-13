from r1cs.r1cs import load_matrices_from_json
import random
from py_ecc.bn128.bn128_curve import G1, G2, multiply, curve_order, add, neg
from keys import keys

class TrustedSetup:

    def __init__(self, example_path='./examples/example1/'):
        self.example_path = example_path

    def get_constraints_number(self):
        L, R, O = load_matrices_from_json(json_path=self.example_path + 'r1cs.json')
        num_constraints = len(L)
        return num_constraints
    


    def power_of_tau_G1(self, constraints_nb, tau):
        powers_of_tau_G1 = [multiply(G1, 1)] 
        degree = constraints_nb -1
        for i in range(0, degree):
            powers_of_tau_G1.append(multiply(powers_of_tau_G1[i], tau))
        return powers_of_tau_G1
    
    def power_of_tau_G2(self, constraints_nb, tau):
        powers_of_tau_G2 = [multiply(G2, 1)]
        degree = constraints_nb -1 
        for i in range(0, degree):
            powers_of_tau_G2.append(multiply(powers_of_tau_G2[i], tau))
        return powers_of_tau_G2

    def calculate_t_at_tau_G1(self, tau, constraints_nb,):
        # t(x) = (x-1)(x-2)...(x - constraints_nb)
        t_at_tau = 1
        for i in range(1, constraints_nb + 1):
            t_at_tau = (t_at_tau * (tau - i)) % curve_order
        t_at_tau_G1 = multiply(G1, t_at_tau)
        
        return t_at_tau_G1



    def power_of_tau_G1_with_t(self, constraints_nb, tau):
        degree = constraints_nb - 2
        t_at_tau_G1 = self.calculate_t_at_tau_G1(tau, constraints_nb)
        powers_of_tau_G1_with_t = [t_at_tau_G1] 
        for i in range(0, degree):
            powers_of_tau_G1_with_t.append(multiply(powers_of_tau_G1_with_t[i], tau))
        return powers_of_tau_G1_with_t

    def generate_srs(self):
        constraints_nb = self.get_constraints_number()
        tau = random.randint(0, curve_order )
        srs1 = self.power_of_tau_G1(constraints_nb, tau)
        srs2 = self.power_of_tau_G2(constraints_nb, tau)
        srs3 = self.power_of_tau_G1_with_t(constraints_nb, tau)

        keys.save_prooving_key_to_json(srs1, srs2, srs3, json_path = self.example_path + 'proving_key.json')


        return srs1, srs2, srs3

    

