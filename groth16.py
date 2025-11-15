import sys
    

def print_usage():
    print('''
    Usage: python verifier.py <command> <example_number:int>
    Commands:
          full - Run the full ZK proof cycle: trusted setup (Reads from r1cs.json, writes proving_key.json and verifying_key.json), 
                 proof generation (Reads from proving_key.json and witness.json, writes proof.json) 
                 and proof verification (Reads from proof.json and verifying_key.json)
          setup - Run the trusted setup phase only for the given example (Reads from r1cs.json, writes proving_key.json and verifying_key.json)
          prove - Generate a proof for the given example (Read from proving_key.json and witness.json, writes proof.json)
          verify - Verify the proof for the given example (Read from proof.json and verifying_key.json)
    Example:
          python verifier.py full 1
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



