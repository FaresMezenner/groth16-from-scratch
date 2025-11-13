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

example_path = f'./examples/example{example_number}/'
if command == 'full' :
    from verifier.verifier import Verifier
    from prover.prover import Prover
    from trusted_setup.trusted_setup import TrustedSetup
    trusted_setup = TrustedSetup(example_path=example_path)
    prover = Prover(example_path=example_path)
    verifier = Verifier(example_path=example_path)
    trusted_setup.generate_srs() 
    prover.generate_proof()
    result = verifier.verify()

elif command == 'setup':
    from trusted_setup.trusted_setup import TrustedSetup
    trusted_setup = TrustedSetup(example_path=example_path)
    trusted_setup.generate_srs()
elif command == 'prove':
    from prover.prover import Prover
    prover = Prover(example_path=example_path)
    prover.generate_proof()
elif command == 'verify':
    from verifier.verifier import Verifier
    verifier = Verifier(example_path=example_path) 
    result = verifier.verify()
else:
    print_usage()
    sys.exit(1)



