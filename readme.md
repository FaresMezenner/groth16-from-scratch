# Hello and welcome to my personal implementation of the the Groth16 algorithm from scratch

Note: All arithmetic in this repository is performed over a finite field $\mathbb{F}_p$. Unless otherwise stated, we use $p=101$ in examples and tests.

For this implementation we will be using the following technologies (This list will be updated as we advance in this repo):

* **Python**
* **PyTest:** for testing different parts of the algorithm as we advance.

This implementation is based on my understanding of the ZK proof concept explained in the [ZK Book](https://rareskills.io/zk-book).

To understand this implementation, you should be familiar with the theory behind ZK proofs, since here I will be writing my understanding of the concepts only, not with the the intention of explaining them from scratch for beginners.

## Working with this repo

### Running the code with different examples

Examples are defined in the `examples/` folder, each example has its own folder named `exampleX` where `X` is the example number.
Each example folder contains the explanation of the example in a `readme.md` file, the witness in a `witness.json` file, and the R1CS matrices in a `r1cs.json` file.
This structure will change as we advance in the implementation.
By the default, the code runs with `example1`:

```bash
python groth16.py full
```

To run with another example, you can provide the example number as a second argument:

```bash
python groth16.py full 2
```

The `full` command is meant to run the full Groth16 proof generation and verification, but at this step we just have the verifier implemented, so it will just run the verifier for now.
Other commands are:

* `setup`: to just setup the example (not implemented yet).
* `prove`: to just run the prover (not implemented yet).
* `verify`: to just run the verifier.

### Tests

To run the tests, you can use the following command:

```bash
python -m unittest discover -s tests
```

These tests are meant to test different parts of the implementation as we advance.

## **Step 1 (We are here so far): R1CS Implementation**

Starting easy, we must first understand and implement **Rank 1 Constrain System (R1CS).**
Basically, in ZK proofs, a verifier has an aricthmetic circuit over a finite field that modelizes computation, a prover having a witness for that circuit means that they have a set of signals for all the wires (public, private, and intermediate ones) that makes all the equations in the circuit evaluate to true. All of this without revealing any information about the private inputs to the verifier.
In this step, we will see how to express any arithmetic circuit as R1CS constraints,

### Defining the witness vector

The witness vector is simply the vector that contains all the wire values (inputs, outputs, and intermediate wires) that satisfy the circuit equations.

* **Inputs:** these are the values that the prover knows and provides them to the verifier.
* **Outputs:** these are the values that the verifier knows (can calculate) but they must be provided by the prover as well, why? so they could prove that they know the inputs that lead to these outputs.
* **Intermediate wires:** these are the values that are computed in the circuit but are neither inputs nor outputs, they are just needed to make the circuit work.

We denote the witness vector as:
$$a = [1, a_1, a_2, a_3, ..., a_n]$$
Where each $a_i$ is the value of wire $i$ in the circuit.
Why is that $1$ at the start? Because in R1CS we always have a constant wire with value $1$ that we use to express constants in the circuit, we will see how later.

### Example: a simple arithmetic circuit

Let's say we want to check if the prover knows values for $x$ and $y$ such that when we compute the following function: $f(x, y) = (x + y) \cdot (x \cdot y) + c$ (where $c$ is a constant), they can provide us with the output $o$.

Our circuit gates are as follows:
$$
z_1 = (x + y)\cdot(x \cdot y)
$$
$$
o = z_1 + c
$$
Witness (over $\mathbb{F}_{101}$) for inputs $x=3$, $y=4$, $c=5$ (in here $c=5$ is a constant):

$$ x = 3 $$

$$ y = 4 $$

$$ z_1 = 84 $$

$$ o = 89 $$

All values are modulo $101$.

So the witness vector will be:
$$a = [1, x, y, z_1, o] = [1, 3, 4, 84, 89]$$
meaning that position $1$ is for $x$, position $2$ is for $y$, position $3$ is for $z_1$, and position $4$ is for $o$.

Notice how $c$ is a constant, not a variable, so we don't need to assign it a wire value in the witness.

Now we want to express this circuit as a Rank 1 Constrain System (R1CS). How we do it? By making each line in the circuit correspond to a constraint in the R1CS form:
<!-- Let w ∈ F^n be the vector of all wires. Pick indices i, j ∈ {1, …, n} and a subset S ⊆ {1, …, n}. The constraint expresses that the product of wires i and j equals the sum of wires in S:

$$
\sum_{k\in S} w_k = w_i \cdot w_j.
$$

The right hande side could also be $0$ if we want to express an addition only.
$$
\sum_{k\in S} w_k = 0.
$$

In other words, each constraint will have: -->

* **In the right hand:** just additions of any set of wires, but ZERO multiplication.
* **In the left hand:** at most one multiplication, and no additions at all.

**IMPORTANT NOTE:** variables could have coefficients, and it is not considered a multiplication if we multiply a variable by a constant, we are talking about multiplication between two variables only.

### Example: The simple arithmetic circuit as R1CS

We can express our previous circuit as the following R1CS constraints:

$$z_1 = x \cdot y$$
$$z_2 - x - y = 0$$
$$o - c = z_1 \cdot z_2$$

If we make the needed substitutions we can see that these constraints are equivalent to our original circuit, and hence the original function that prover wants to proof to us the he knows a set of values that satisfy it (both inputs and outputs).
This example might seem trivial, but it is important to understand how to express any circuit as R1CS constraints, as this is the first step towards implementing Groth16 ZK proofs, we will see more practical and complicated examples later.

### Defining L, R, O matrices

Now that we have our R1CS constraints, we want to express them in a matrix form, and that's the last step for the R1CS implementation step.
Each one of them has the dimensions (number of constraints) x (number of wires).

#### The L matrix

**L** stands for **Left**.
To build it, we focus on the left hand side of each multiplication in each constraint $i$, we look at which wires are being multiplied, and for each wire $j$ that is being multiplied in that constraint, we put its coefficient in the matrix cell $L[i][j]$.
Meaning if we have one constraint like $z = 2x \cdot y$ we put $2$ in the cell $L[0][1]$ giving that $x$ is wire $1$ and $y$ is wire $2$ and $z$ is wire $3$.

#### The R matrix

**R** stands for **Right**.
We apply the same logic as in the L matrix, but now we focus on the right hand side of each multiplication in each constraint.

#### The O matrix

**O** stands for **Output**.
Now we focus on the left hand side of each constraint $i$, which is the addition part.
To build it, we look at which wires are being added, and for each wire $j$ that is being added in that constraint, we put its coefficient in the matrix cell $O[i][j]$.
Meaning if we have one constraint like $a+2b= x \cdot y$ we put $1$ in the cell $O[0][1]$ (for wire $a$) and $2$ in the cell $O[0][2]$ (for wire $b$) and $0$ wlsewhere.

#### Using the matrices

Like this, we will express all of our R1CS constraints in matrix form, which will be useful later on in the Groth16 implementation.
How does it look? it is exactly like this:

$$
O\,a = (L\,a)\odot(R\,a)
$$
where $a$ is the witness vector, $L$, $R$, and $O$ are the matrices we just defined, and $\odot$ is the Hadamard product (element-wise multiplication).

### Example: Building L, R, O matrices for our example

Let's build the L, R, O matrices for our previous example with the following constraints:

$$z_1 = x \cdot y$$
$$z_2 - x - y = 0$$
$$o - c = z_1 \cdot z_2$$

Our witnes vector $a$ is: $$a = [1, x, y, z_1, z_2, o]$$.
Each matrix will have $3$ rows (one for each constraint) and $6$ columns (one for each wire).

**PS:** for the second constraint, we could also write it as:
$$z_2 - x = y$$
Since the right hand side must have at most one multiplication, we could consider $y$ as being multiplied by $1$.

#### Defining the L and R matrix

Focusing on the left hand side of each multiplication of each constraint:

* **Contraint 1:** we have $x \cdot y$, so we put $1$ in cell $L[0][1]$ (for wire $x$) and $1$ in cell $R[0][2]$ (for wire $y$).
* **Constraint 2:** there is no multiplication on the left hand side, so the entire row $1$ in both L and R matrices will be $0$s. For the case of $z_2 - x = y$, we would put $1$ for $y$ in the $L$ matrix (hence in $L[1][2]$), and $1$ for the constant $1$ in the $R$ matrix (hence in $R[1][0]$), but we will keep it as is for simplicity.
* **Constraint 3:** we have $z_1 \cdot z_2$, so we put $1$ in cell $L[2][3]$ (for wire $z_1$) and $1$ in cell $R[2][4]$ (for wire $z_2$).

#### Defining the O matrix

Focusing on the left hand side of each constraint (the addition part):

* **Constraint 1:** we have $z_1$ alone on the left hand side, so we put $1$ in cell $O[0][3]$ (for wire $z_1$).
* **Constraint 2:** we have $z_2 - x - y = 0$, so we put $1$ in cell $O[1][4]$ (for wire $z_2$), $-1$ in cell $O[1][1]$ (for wire $x$), and $-1$ in cell $O[1][2]$ (for wire $y$). For the case of $z_2 - x = y$, we would put $0$ for $y$ in the $O$ matrix (hence in $O[1][2]$) instead.
* **Constraint 3:** we have $o - c$ on the left hand side, so we put $1$ in cell $O[2][5]$ (for wire $o$), and $-c$ in cell $O[2][0]$ (for the constant wire, because $c$ is constant, so techincally it is the coefficient of the constant wire $1$).

Final matrices:

$$
L = \begin{bmatrix}
0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0
\end{bmatrix}
\qquad
R = \begin{bmatrix}
0 & 0 & 1 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0
\end{bmatrix}
\qquad
O = \begin{bmatrix}
0 & 0 & 0 & 1 & 0 & 0 \\
-c & -1 & -1 & 0 & 1 & 0 \\
0 & 0 & 0 & 0 & 0 & 1
\end{bmatrix}
$$

and using them, our R1CS example will be expressed as:
$$
O\,a = (L\,a)\odot(R\,a)
$$

when $a$ is the witness vector defined before.
if we expand both sides, we get the same constraints we defined previously, you can check it yourself!.
and that's how we define R1CS for any arithmetic circuit.
The problems we have now are that there is no ZK mechanisms yet, and the operations with matrices are expensive, so in the next steps we will see how Groth16 helps us to solve these problems.
