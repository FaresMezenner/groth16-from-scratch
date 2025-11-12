import unittest
from unittest.mock import patch, mock_open
from r1cs.r1cs import load_matrices_from_json


class TestR1CS(unittest.TestCase):

    @patch("r1cs.r1cs.json.load")
    @patch("r1cs.r1cs.open", new_callable=mock_open, read_data='{}')
    def test_load_matrices_from_json(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "L": [[1, 2, 3], [4, 5, 6]],
            "R": [[7, 8, 9], [10, 11, 12]],
            "O": [[13, 14, 15], [16, 17, 18]]
        }

        L, R, O = load_matrices_from_json("dummy_path.json")

        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()
        self.assertEqual(L, [[1, 2, 3], [4, 5, 6]])
        self.assertEqual(R, [[7, 8, 9], [10, 11, 12]])
        self.assertEqual(O, [[13, 14, 15], [16, 17, 18]])


    @patch("r1cs.r1cs.json.load")
    @patch("r1cs.r1cs.open", new_callable=mock_open, read_data='{}')
    def test_load_matrices_mismatched_rows(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "L": [[1, 2, 3], [4, 5, 6]],  # 2 rows
            "R": [[7, 8, 9]],  # 1 row
            "O": [[10, 11, 12], [13, 14, 15]]  # 2 rows
        }

        with self.assertRaises(AssertionError) as context:
            load_matrices_from_json("dummy_path.json")

        self.assertIn("L, R, O must have the same number of rows", str(context.exception))
        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()


    @patch("r1cs.r1cs.json.load")
    @patch("r1cs.r1cs.open", new_callable=mock_open, read_data='{}')
    def test_load_matrices_inconsistent_L_columns(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "L": [[1, 2, 3], [4, 5]],  # L rows have different column counts
            "R": [[6, 7, 8], [9, 10, 11]],
            "O": [[12, 13, 14], [15, 16, 17]]
        }

        with self.assertRaises(AssertionError) as context:
            load_matrices_from_json("dummy_path.json")

        self.assertIn("All rows in L must have the same number of columns", str(context.exception))
        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()


    @patch("r1cs.r1cs.json.load")
    @patch("r1cs.r1cs.open", new_callable=mock_open, read_data='{}')
    def test_load_matrices_inconsistent_R_columns(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "L": [[1, 2, 3], [4, 5, 6]],
            "R": [[7, 8, 9], [10, 11]],  # R rows have different column counts
            "O": [[12, 13, 14], [15, 16, 17]]
        }

        with self.assertRaises(AssertionError) as context:
            load_matrices_from_json("dummy_path.json")

        self.assertIn("All rows in R must have the same number of columns", str(context.exception))
        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()


    @patch("r1cs.r1cs.json.load")
    @patch("r1cs.r1cs.open", new_callable=mock_open, read_data='{}')
    def test_load_matrices_inconsistent_O_columns(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "L": [[1, 2, 3], [4, 5, 6]],
            "R": [[7, 8, 9], [10, 11, 12]],
            "O": [[13, 14, 15], [16, 17]]  # O rows have different column counts
        }

        with self.assertRaises(AssertionError) as context:
            load_matrices_from_json("dummy_path.json")

        self.assertIn("All rows in O must have the same number of columns", str(context.exception))
        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()


    @patch("r1cs.r1cs.json.load")
    @patch("r1cs.r1cs.open", new_callable=mock_open, read_data='{}')
    def test_load_empty_matrices(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "L": [],
            "R": [],
            "O": []
        }

        with self.assertRaises(AssertionError) as context:
            load_matrices_from_json("dummy_path.json")

        self.assertIn("Matrices L, R, O cannot be empty", str(context.exception))
        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()


    @patch("r1cs.r1cs.json.load")
    @patch("r1cs.r1cs.open", new_callable=mock_open, read_data='{}')
    def test_load_matrices_with_empty_rows(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "L": [[]],
            "R": [[]],
            "O": [[]]
        }

        with self.assertRaises(AssertionError) as context:
            load_matrices_from_json("dummy_path.json")

        self.assertIn("Matrices L, R, O cannot be empty", str(context.exception))
        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()


    @patch("r1cs.r1cs.json.load")
    @patch("r1cs.r1cs.open", new_callable=mock_open, read_data='{}')
    def test_load_matrices_missing_key(self, mock_file, mock_json_load):
        mock_json_load.return_value = {
            "L": [[1, 2, 3]],
            "R": [[4, 5, 6]]
        }

        with self.assertRaises(KeyError):
            load_matrices_from_json("dummy_path.json")

        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()
