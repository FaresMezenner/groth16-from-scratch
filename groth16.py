import sys
    

def print_usage():
    print('''
    Usage: python verifier.py <command> <example_number:int>
    Commands:
          full - Run the full ZK proof (currently only verifier part is implemented with no ZK properties)
          setup - Run the trusted setup phase (not implemented yet)
          prove - Generate a proof for the given example (not implemented yet)
          verify - Verify the proof for the given example (no ZK properties yet)
''')

if len(sys.argv) < 2:
    print_usage()
    sys.exit(1)

command = sys.argv[1]
example_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1

if command == 'full' or command == 'verify':
    from verifier.verifier import VerifierNoZK
    verifier = VerifierNoZK(modulo=101, example_path=f'./examples/example{example_number}/') 
    try:
        result = verifier.verify_proof_r1cs_no_zk()
        if result:
            print("Verification succeeded.")
        else:
            print("Verification failed.")
    except AssertionError as e:
        print(f"Verification failed: {e}")
else:
    print_usage()
    sys.exit(1)



