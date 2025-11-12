import unittest
from unittest.mock import patch
from verifier.verifier import VerifierNoZK


class TestVerifier(unittest.TestCase):

    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_valid_single_constraint(self, mock_load_matrices, mock_load_witness):
        # witness: [1, x=3, y=4, z=12]
        # constraint: z = x * y => 12 = 3 * 4
        mock_load_witness.return_value = [1, 3, 4, 12]
        mock_load_matrices.return_value = (
            [[0, 1, 0, 0]],  # L
            [[0, 0, 1, 0]],  # R
            [[0, 0, 0, 1]]   # O
        )
        
        verifier = VerifierNoZK(modulo=101)
        result = verifier.verify_proof_r1cs_no_zk()
        
        self.assertTrue(result)
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_valid_multiple_constraints(self, mock_load_matrices, mock_load_witness):
        # witness: [1, x=2, y=3, z1=6, z2=9]
        # constraint 1: z1 = x * y => 6 = 2 * 3
        # constraint 2: z2 - y= z1 => 9 - 3 = 6
        mock_load_witness.return_value = [1, 2, 3, 6, 9]
        mock_load_matrices.return_value = (
            [[0, 1, 0, 0, 0], [0, 0, 0, 1, 0]],  # L
            [[0, 0, 1, 0, 0], [1, 0, 0, 0, 0]],  # R
            [[0, 0, 0, 1, 0], [0, 0, -1, 0, 1]]  # O 
        )
        
        verifier = VerifierNoZK(modulo=101)
        result = verifier.verify_proof_r1cs_no_zk()
        
        self.assertTrue(result)
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_failed_verification(self, mock_load_matrices, mock_load_witness):
        # Test when O*a != (L*a) ⊙ (R*a)
        mock_load_witness.return_value = [1, 2, 3]
        mock_load_matrices.return_value = (
            [[1, 2, 3]],  # L
            [[1, 2, 3]],  # R
            [[1, 1, 1]]   # O
        )
        
        verifier = VerifierNoZK(modulo=101)
        with self.assertRaises(AssertionError) as context:
            verifier.verify_proof_r1cs_no_zk()
        
        self.assertIn("R1CS verification failed", str(context.exception))
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_mismatched_witness_matrix_dimensions(self, mock_load_matrices, mock_load_witness):
        
        mock_load_witness.return_value = [1, 2, 3] 
        mock_load_matrices.return_value = (
            [[1, 2, 3, 4], [5, 6, 7, 8]],  # L 
            [[9, 10, 11, 12], [13, 14, 15, 16]],  # R
            [[17, 18, 19, 20], [21, 22, 23, 24]]  # O
        )
        
        verifier = VerifierNoZK(modulo=101)
        with self.assertRaises(AssertionError) as context:
            verifier.verify_proof_r1cs_no_zk()
        
        self.assertIn("All rows in the matrices L, R, and O, must have the same number of columns as witness length", str(context.exception))
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_with_zero_values(self, mock_load_matrices, mock_load_witness):
      
        # witness: [ 1, x=0, y=5, z=0]
        # constraint: z = x * y => 0 = 0 * 5
        mock_load_witness.return_value = [1, 0, 5, 0]
        mock_load_matrices.return_value = (
            [[0, 1, 0, 0]],  # L
            [[0, 0, 1, 0]],  # R
            [[0, 0, 0, 1]]   # O
        )
        
        verifier = VerifierNoZK(modulo=101)
        result = verifier.verify_proof_r1cs_no_zk()
        
        self.assertTrue(result)
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_with_negative_values(self, mock_load_matrices, mock_load_witness):
        #  (in finite field arithmetic)
        # witness: [1, -2, 3, -6]
        # constraint: z = x * y => -6 = -2 * 3
        mock_load_witness.return_value = [1, -2, 3, -6]
        mock_load_matrices.return_value = (
            [[0, 1, 0, 0]],  # L
            [[0, 0, 1, 0]],  # R
            [[0, 0, 0, 1]]   # O
        )
        
        verifier = VerifierNoZK(modulo=101)
        result = verifier.verify_proof_r1cs_no_zk()
        
        self.assertTrue(result)
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_with_modulo_17(self, mock_load_matrices, mock_load_witness):
        # witness: [1, x=5, y=4, z=3]
        # constraint: z = x * y => 3 = 5 * 4 ≡ 20 (mod 17)
        mock_load_witness.return_value = [1, 5, 4, 3]
        mock_load_matrices.return_value = (
            [[0, 1, 0, 0]],  # L: selects x=5
            [[0, 0, 1, 0]],  # R: selects y=4
            [[0, 0, 0, 1]]   # O: selects z=3
        )
        
        verifier = VerifierNoZK(modulo=17)
        result = verifier.verify_proof_r1cs_no_zk()
        
        self.assertTrue(result)
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_with_large_modulo(self, mock_load_matrices, mock_load_witness):
        # Test with a larger modulo
        # witness: [1, 100, 200, 20000] where 100*200 = 20000
        mock_load_witness.return_value = [1, 100, 200, 20000]
        mock_load_matrices.return_value = (
            [[0, 1, 0, 0]],  # L: selects x=100
            [[0, 0, 1, 0]],  # R: selects y=200
            [[0, 0, 0, 1]]   # O: selects z=20000
        )
        
        verifier = VerifierNoZK(modulo=1000000007)  # Large prime
        result = verifier.verify_proof_r1cs_no_zk()
        
        self.assertTrue(result)
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


    @patch("verifier.verifier.load_witness_from_json")
    @patch("verifier.verifier.load_matrices_from_json")
    def test_verify_proof_modulo_wrapping(self, mock_load_matrices, mock_load_witness):
        # Test that modulo wrapping works correctly
        # witness: [1, 10, 12, 4] where 10*12 = 120 ≡ 4 (mod 29)
        mock_load_witness.return_value = [1, 10, 12, 4]
        mock_load_matrices.return_value = (
            [[0, 1, 0, 0]],  # L: selects x=10
            [[0, 0, 1, 0]],  # R: selects y=12
            [[0, 0, 0, 1]]   # O: selects z=4
        )
        
        verifier = VerifierNoZK(modulo=29)
        result = verifier.verify_proof_r1cs_no_zk()
        
        self.assertTrue(result)
        mock_load_witness.assert_called_once()
        mock_load_matrices.assert_called_once()


