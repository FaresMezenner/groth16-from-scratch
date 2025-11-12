import unittest
from unittest.mock import patch, mock_open
from witness.witness import load_witness_from_json

class TestWitness(unittest.TestCase):

    
    @patch("witness.witness.json.load") # this is to mock json.load function (no json parsing)
    @patch("witness.witness.open", new_callable=mock_open, read_data='{"a": 1}') # this mocks files opening itself
    def test_load_witness_from_json(self, mock_file, mock_json_load):
        # here we will mock the date returned by json.load
        # we already mocked the file opening, so no file will be read
        # we mocked file loading with a dummy json, but it won't be used, because we mock json.load itself here
        mock_json_load.return_value = [1, 2, 3, 4]

        result = load_witness_from_json("dummy_path.json")

        # assertions
        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()
        self.assertEqual(result, [1, 2, 3, 4])



    @patch("witness.witness.json.load") 
    @patch("witness.witness.open", new_callable=mock_open, read_data='{"a": 1}')
    def test_load_empty_witness_from_json(self, mock_file, mock_json_load):
        # Test loading an empty witness from JSON - should raise AssertionError
        mock_json_load.return_value = []

        with self.assertRaises(AssertionError) as context:
            load_witness_from_json("dummy_path.json")

        self.assertIn("Witness cannot be empty", str(context.exception))
        mock_file.assert_called_once_with("dummy_path.json", 'r')
        mock_json_load.assert_called_once()






