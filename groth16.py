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

if command == 'full' :
    from verifier.verifier import Verifier
    from prover.prover import Prover
    prover = Prover(example_path=f'./examples/example{example_number}/')
    verifier = Verifier(modulo=101, example_path=f'./examples/example{example_number}/') 
    prover.generate_somewhate_zk_proof_r1cs()
    result = verifier.verify_somewhat_zk_proof()
elif command == 'prove':
    from prover.prover import Prover
    prover = Prover(example_path=f'./examples/example{example_number}/')
    prover.generate_somewhate_zk_proof_r1cs()
elif command == 'verify':
    from verifier.verifier import Verifier
    verifier = Verifier(modulo=101, example_path=f'./examples/example{example_number}/') 
    result = verifier.verify_somewhat_zk_proof()
else:
    print_usage()
    sys.exit(1)



