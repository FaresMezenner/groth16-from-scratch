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
* `prove`: to just run the prover and generates `somewhat_zk_proof_witness.json` by using `wintess.json`.
* `verify`: to just run the verifier, it reads `somewhat_zk_proof_witness.json` and `r1cs.json`.

## **Step 1 (implementation at [c246b8a](https://github.com/FaresMezenner/groth16-from-scratch/commit/c246b8a1b15ffe5f0f591c626a76ba15537a3210)): R1CS Implementation**

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

## Step 2 (We are here so far): Somewhat ZK proof using R1CS

Previously, we created a R1CS representation of an arithmetic circuit that verifies that a prover knows a witness that satisfies the circuit constraints (what we want to verify, in other words).

But it was not zero-knowledge at all, since the verifier could see all the witness values.
So what will we do? we will create a "somewhat" zero-knowledge proof, meaning that the verifier will not see the actual witness values, but they will be able to verify that the prover knows a witness that satisfies the circuit constraints.
And how? by encrypting the wintess values, and doing all the operations in the **ECC (Elliptic Curve Cryptography)** encrypted domain.

So this will happen:

* Instead of sending the witness values directly to the verifier, the prover will send their ECC encrypted versions, by multiplying all the values of the witness with the generator points of the ECC groups $ \mathbb{G}_1$  and  $\mathbb{G}_2 $.
* We will replace the Hadamard product in the R1CS equation with the ECC pairing operation, which results in a $\mathbb{G}_T$ which is a group of elements with $12$ dimensions.

### Calculations

#### Encrypting the witness

The prover has the witness vector $a = [1, a_1, a_2, ..., a_n]$, to encrypt it, they will compute two new vectors:

$$
w_{g1} = [G_1, a_1 \cdot G_1, a_2 \cdot G_1, ..., a_n \cdot G_1]
$$

$$
w_{g2} = [G_1, a_1 \cdot G_1, a_2 \cdot G_1, ..., a_n \cdot G_1]
$$

Where $G_1$ and $G_2$ are the generator points of the ECC groups $\mathbb{G}_1$ and $\mathbb{G}_2$ respectively.

Why do we need two encrypted witness vectors? because the pairing operation takes one element from $\mathbb{G}_1$ and one from $\mathbb{G}_2$, so we need both, one the $L$ matrix, and the other for the $R$ matrix.
This calculation is done by the prover.

#### Verifying the encrypted witness

This is done by the verifier.
We need to verifty that the prover actually encrypted the same witness in both $w_{g1}$ and $w_{g2}$ to avoid melicious behavior.
This is done by pairing $w_{g1}$ elements with $G_2$ generator point, and pairing $w_{g2}$ elements with $G_1$ generator point, and checking that the results are equal for each index:
$$
e(w_{g1}[i], G_1) = e(G_1, w_{g2}[i]) \quad \forall i \in [0, n]
$$

**NOTATION NOTE:** $e()$ is the pairing operation, it takes one element from $\mathbb{G}_1$ and one from $\mathbb{G}_2$, and returns an element in $\mathbb{G}_T$. For easier notation, we will denote it using $ \odot $ from now on.

#### Verifying the R1CS constraints in the encrypted domain

We will calculate multiplications with $L$, $R$, $O$ as following:

* **L:** Same calulcations as earlier, but replace each multiplication by the pairing operation, and it will be done between $L$ and $w_{g1}$, the result is $L\,w_{g1}$
* **R:** Same calulcations as earlier, but replace each multiplication by the pairing operation, and it will be done between $L$ and $w_{g2}$, the result is $R\,w_{g2}$
* **Hadamard product between $L\,w_{g1}$ and $R\,w_{g2}$:** Same as earlier, but now instead of multiplication we will have pairing, and the values will be in $\mathbb{G}_T$.
* **O:** Here, we do the same calculations as earlier, but we need to be careful, because the results of the $L\,w_{g1}$ and $R\,w_{g2}$ pairing are in $\mathbb{G}_T$, so we need to get $O$ to have values in $\mathbb{G}_T$ as well, to do that, we will multiply $O$ matrix by $w_{g1}$, the result is $O\,w_{g1}$, and now to jump to $\mathbb{G}_T$, we will pair the result with $G_2$ generator point, meaning each value in $O\,w_{g1}$ will be paired with $G_2$, the results will be in $\mathbb{G}_T$.

You might ask, why does not the prover multiply $O$ with $G_T$, the generator point of $\mathbb{G}_T$, and then sends it to the verifier directly? Well, we do not do this because it is impractical, because the prover would need to send elements in the $\mathbb{G}_T$ group, which are $12$-dimensional, meaning that each element would be represented by $12$ points in the ECC curve, which is a lot of data to send, so we avoid this by making the verifier do the pairing with $G_1$ and then $G_2$.

Finally, the verifier checks that:
$$
O\,w_{g1} \odot G_2 = (L\,w_{g1}) \odot (R\,w_{g2})
$$

Where $\odot$ is the pairing operation.

### What needs to be fixed so far

So far, we have a "somewhat" zero-knowledge proof, why "somewhat"? because the verifier could still learn some information about the witness, for example, if the witness values are small, the verifier could brute-force them by trying all possible values and checking if they satisfy the constraints.

The construction is also not succinct, because the verifier needs to do a lot of calculations, especially with the matrices.
