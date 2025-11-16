from galois import GF
from r1cs.r1cs import load_matrices_from_json
import random
from py_ecc.bn128.bn128_curve import G1, G2, multiply, curve_order, add, neg
from keys import keys
from utils import utils
from witness import witness

class TrustedSetup:

    def __init__(self, example_path='./examples/example1/'):
        self.example_path = example_path

    def get_constraints_number(self, L):
        num_constraints = len(L)
        num_variables = len(L[0])
        return num_constraints, num_variables
    


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



    def power_of_tau_G1_with_t(self, constraints_nb, tau, delta):
        degree = constraints_nb - 2
        t_at_tau_G1 = self.calculate_t_at_tau_G1(tau, constraints_nb)
        t_at_tau_G1 = multiply(t_at_tau_G1, pow(delta, -1, curve_order))
        powers_of_tau_G1_with_t = [t_at_tau_G1] 
        for i in range(0, degree):
            powers_of_tau_G1_with_t.append(multiply(powers_of_tau_G1_with_t[i], tau))
        return powers_of_tau_G1_with_t

    def calculate_psi_values(self,  L, R, O,tau, num_polynomials, alpha, beta, num_public_inputs, delta, gamma):

        galois_field = GF(curve_order)

        # Generate the polynomials of the matrices using Lagrange interpolation
        L_transposed = list(zip(*L))
        R_transposed = list(zip(*R))
        O_transposed = list(zip(*O))
        
        # Convert tau, alpha, beta to field elements so all ops remain in GF
        tau_field = galois_field(tau)
        alpha_field = galois_field(alpha)
        beta_field  = galois_field(beta)

        L_polys = [utils.lagrange_poly_vector(col, galois_field=galois_field) for col in L_transposed]
        R_polys = [utils.lagrange_poly_vector(col, galois_field=galois_field) for col in R_transposed]
        O_polys = [utils.lagrange_poly_vector(col, galois_field=galois_field) for col in O_transposed]

        psi_values = []
        for i in range(num_polynomials):
            alpha_v_i_tau = alpha_field * R_polys[i](tau_field)
            beta_u_i_tau = beta_field * L_polys[i](tau_field)
            psi_i = multiply(G1, int(alpha_v_i_tau + beta_u_i_tau + O_polys[i](tau_field)))
            if i < num_public_inputs:
                psi_i = multiply(psi_i, pow(gamma, -1, curve_order))
            else:
                psi_i = multiply(psi_i, pow(delta, -1, curve_order))
            psi_values.append(psi_i)

        return psi_values




    def generate_srs(self):
        L, R, O = load_matrices_from_json(json_path=self.example_path + 'r1cs.json', galois_field=GF(curve_order))
        constraints_nb, num_variables = self.get_constraints_number(L)
        num_public_inputs = witness.public_inputs_length(
            json_path=self.example_path + 'public_witness.json'
        )

        tau = random.randint(1, curve_order )
        alpha = random.randint(1, curve_order )
        beta = random.randint(1, curve_order )
        delta = random.randint(1, curve_order )
        gamma = random.randint(1, curve_order )

        srs1 = self.power_of_tau_G1(constraints_nb, tau)
        srs2 = self.power_of_tau_G2(constraints_nb, tau)
        srs3 = self.power_of_tau_G1_with_t(constraints_nb, tau, delta)
        
        psi = self.calculate_psi_values(L, R, O, tau, num_variables, alpha, beta, num_public_inputs, delta, gamma)

        # take only the first num_public_inputs values of psi for verifying key
        verifying_psi = psi[:num_public_inputs ]
        proving_psi = psi[num_public_inputs:]

        alpha_G1 = multiply(G1, alpha)
        beta_G2 = multiply(G2, beta)
        delta_G2 = multiply(G2, delta)
        gamma_G2 = multiply(G2, gamma)

        keys.save_prooving_key_to_json(srs1, srs2, srs3, proving_psi, alpha_G1, beta_G2, json_path = self.example_path + 'proving_key.json')
        keys.save_verifying_key_to_json( alpha_G1, beta_G2, delta_G2, gamma_G2, verifying_psi, json_path = self.example_path + 'verifying_key.json')

        return srs1, srs2, srs3, psi

    

