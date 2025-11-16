# Hello and welcome to my personal implementation of the the Groth16 algorithm from scratch


Note: All arithmetic in this repository is performed over a finite field $\mathbb{F}_p$. Unless otherwise stated, we use $p=101$ in examples and tests.


For this implementation we will be using the following technologies (This list will be updated as we advance in this repo):

* **Python:** used version $3.13.2$.
* **py_ecc**
* **galois**

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
* `prove`: to just run the prover and generates `somewhat_zk_proof_witness.json` by using `witness.json`.
* `verify`: to just run the verifier, it reads `somewhat_zk_proof_witness.json` and `r1cs.json`.


## **Step 1 (implementation at [c246b8a](https://github.com/FaresMezenner/groth16-from-scratch/commit/c246b8a1b15ffe5f0f591c626a76ba15537a3210)): R1CS Implementation**


Starting easy, we must first understand and implement **Rank 1 Constrain System (R1CS).**
Basically, in ZK proofs, a verifier has an arithmetic circuit over a finite field that modelizes computation, a prover having a witness for that circuit means that they have a set of signals for all the wires (public, private, and intermediate ones) that makes all the equations in the circuit evaluate to true. All of this without revealing any information about the private inputs to the verifier.
In this step, we will see how to express any arithmetic circuit as R1CS constraints,


### Defining the witness vector


The witness vector is simply the vector that contains all the wire values (inputs, outputs, and intermediate wires) that satisfy the circuit equations.


* **Inputs:** these are the values that the prover knows and provides them to the verifier.
* **Outputs:** these are the values that the verifier knows (can calculate) but they must be provided by the prover as well, why? so they could prove that they know the inputs that lead to these outputs.
* **Intermediate wires:** these are the values that are computed in the circuit but are neither inputs nor outputs, they are just needed to make the circuit work.


We denote the witness vector as:


$$
a = [1, a_1, a_2, a_3, ..., a_n]
$$


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


$$
x = 3
$$


$$
y = 4
$$


$$
z_1 = 84
$$


$$
o = 89
$$


All values are modulo $101$.


So the witness vector will be:


$$
a = [1, x, y, z_1, o] = [1, 3, 4, 84, 89]
$$


meaning that position $1$ is for $x$, position $2$ is for $y$, position $3$ is for $z_1$, and position $4$ is for $o$.


Notice how $c$ is a constant, not a variable, so we don't need to assign it a wire value in the witness.


Now we want to express this circuit as a Rank 1 Constrain System (R1CS). How we do it? By making each line in the circuit correspond to a constraint in the R1CS form:


* **In the right hand:** just additions of any set of wires, but ZERO multiplication.
* **In the left hand:** at most one multiplication, and no additions at all.


**IMPORTANT NOTE:** variables could have coefficients, and it is not considered a multiplication if we multiply a variable by a constant, we are talking about multiplication between two variables only.


### Example: The simple arithmetic circuit as R1CS


We can express our previous circuit as the following R1CS constraints:


$$
z_1 = x \cdot y
$$


$$
z_2 - x - y = 0
$$


$$
o - c = z_1 \cdot z_2
$$


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


$$
z_1 = x \cdot y
$$


$$
z_2 - x - y = 0
$$


$$
o - c = z_1 \cdot z_2
$$


Our witnes vector $a$ is:


$$
a = [1, x, y, z_1, z_2, o]
$$


.
Each matrix will have $3$ rows (one for each constraint) and $6$ columns (one for each wire).


**PS:** for the second constraint, we could also write it as:


$$
z_2 - x = y
$$


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
L = \left[
\begin{array}{cccccc}
0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0
\end{array}
\right]
\qquad
R = \left[
\begin{array}{cccccc}
0 & 0 & 1 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0
\end{array}
\right]
\qquad
O = \left[
\begin{array}{cccccc}
0 & 0 & 0 & 1 & 0 & 0 \\
-c & -1 & -1 & 0 & 1 & 0 \\
0 & 0 & 0 & 0 & 0 & 1
\end{array}
\right]
$$


and using them, our R1CS example will be expressed as:


$$
O\,a = (L\,a)\odot(R\,a)
$$


when $a$ is the witness vector defined before.
if we expand both sides, we get the same constraints we defined previously, you can check it yourself!.
and that's how we define R1CS for any arithmetic circuit.
The problems we have now are that there is no ZK mechanisms yet, and the operations with matrices are expensive, so in the next steps we will see how Groth16 helps us to solve these problems.


## Step 2 (implementation at [677ee43](https://github.com/FaresMezenner/groth16-from-scratch/commit/677ee437ae3d84f394ef24b9939fc093963dd8dc)): Somewhat ZK proof using R1CS


Previously, we created a R1CS representation of an arithmetic circuit that verifies that a prover knows a witness that satisfies the circuit constraints (what we want to verify, in other words).


But it was not zero-knowledge at all, since the verifier could see all the witness values.
So what will we do? we will create a "somewhat" zero-knowledge proof, meaning that the verifier will not see the actual witness values, but they will be able to verify that the prover knows a witness that satisfies the circuit constraints.
And how? by encrypting the winneress values, and doing all the operations in the **ECC (Elliptic Curve Cryptography)** encrypted domain.


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


## Step 3 (implementation at [02a57a9](https://github.com/FaresMezenner/groth16-from-scratch/commit/02a57a9fe9d6390491c3aa5673dd31d2d00ae672)): Succinct ZK proof using QAP (Quadratic Arithmetic Programs)


By succinct, means that the proof can be verified clearly and quickly.


Quadratic Arithmetic Programs (QAP) are a way to represent R1CS constraints as polynomials, which allows us to create succinct ZK proofs.


Currently our ZK proof algorithm takes $O(n*m)$ time where $n$ is the number of variables and $m$ is the number of constraints, which is not succinct at all.
How can we make it happen in $O(1)$? Using **Schwartz-Zippel Lemma**, wich tells us that two non equivalent polynomials are equal in very few points, and exactly the number of these points is as maximum as the larger degree of the two polynomials. So we could use the **lemma** to check that polynomials are equal if they are equal in a random point. But what if we select the point where they are equal even if they are not equivalent? well here we count on probabilities, if the polynomials are of a certain degree, and the finite field order is very large, the chances of selecting such a point are very low.


But Fares, we do not have polynomials, we have matrices!!! Here where Lagrange Interpolation comes into play.
Using Lagrange Interpolation, we could represent the matrices as polynomials, these polynomials will have a degree that is way smaller than the field order, how do we know? Because we will use it to represent each column of the matrices, the degree of each polynomial will be at most the number of constraints, which are way smaller than the field order.


Let's say we have one million variables and one million constraints, the degree of the polynomials will be at most one million, so we will be comparing polynomials of degree one million, in a field of order $p$, let's say $p$ is a 256-bit prime ($\approx 10^{77}$), the chances of selecting a random point where two non equivalent polynomials of degree one million are equal is at most


$$
\frac{10^6}{10^{77}} = 10^{-71}
$$


 which is very low.


**Enough talking, let's see how it is done!**


### Representing the matrices as polynomials


For this, we will represent each column of the matrix as a polynomial, and then the set of these polynomials will represent the entire matrix. We can add them together to have one polynomial for the entire matrix, but in our case we will keep them separate for easier calculations later.


We know that in interploation, we need to have some points, and then we can build the polynomial that passes through these points.
But in our case we have a vector of values (columns of the matrices), how can we get points from it? We will do it by creating points from the values, where the x-coordinate is the index of the value in the vector, and the y-coordinate is the value itself.
Meaning, if, for example, for $4$ constraints and $4$ wires, we have the following representations:


$$
L = \left[
\begin{array}{cccc}
l_{11} & l_{12} & l_{13} & l_{14} \\
l_{21} & l_{22} & l_{23} & l_{24} \\
l_{31} & l_{32} & l_{33} & l_{34} \\
l_{41} & l_{42} & l_{43} & l_{44}
\end{array}
\right]
\quad
R = \left[
\begin{array}{cccc}
r_{11} & r_{12} & r_{13} & r_{14} \\
r_{21} & r_{22} & r_{23} & r_{24} \\
r_{31} & r_{32} & r_{33} & r_{34} \\
r_{41} & r_{42} & r_{43} & r_{44}
\end{array}
\right]
\quad
O = \left[
\begin{array}{cccc}
o_{11} & o_{12} & o_{13} & o_{14} \\
o_{21} & o_{22} & o_{23} & o_{24} \\
o_{31} & o_{32} & o_{33} & o_{34} \\
o_{41} & o_{42} & o_{43} & o_{44}
\end{array}
\right]
$$


We will represent each column as a polynomial as following:


$$
u_1(x): \mathcal{L}([(1, l_{11}), (2, l_{21}), (3, l_{31}), (4, l_{41})])
\quad
v_1(x): \mathcal{L}([(1, r_{11}), (2, r_{21}), (3, r_{31}), (4, r_{41})])
\quad
w_1(x): \mathcal{L}([(1, o_{11}), (2, o_{21}), (3, o_{31}), (4, o_{41})])
$$


$$
u_2(x): \mathcal{L}([(1, l_{12}), (2, l_{22}), (3, l_{32}), (4, l_{42})])
\quad
v_2(x): \mathcal{L}([(1, r_{12}), (2, r_{22}), (3, r_{32}), (4, r_{42})])
\quad
w_2(x): \mathcal{L}([(1, o_{12}), (2, o_{22}), (3, o_{32}), (4, o_{42})])
$$


$$
u_3(x): \mathcal{L}([(1, l_{13}), (2, l_{23}), (3, l_{33}), (4, l_{43})])
\quad
v_3(x): \mathcal{L}([(1, r_{13}), (2, r_{23}), (3, r_{33}), (4, r_{43})])
\quad
w_3(x): \mathcal{L}([(1, o_{13}), (2, o_{23}), (3, o_{33}), (4, o_{43})])
$$


$$
u_4(x): \mathcal{L}([(1, l_{14}), (2, l_{24}), (3, l_{34}), (4, l_{44})])
\quad
v_4(x): \mathcal{L}([(1, r_{14}), (2, r_{24}), (3, r_{34}), (4, r_{44})])
\quad
w_4(x): \mathcal{L}([(1, o_{14}), (2, o_{24}), (3, o_{34}), (4, o_{44})])
$$


Where $\mathcal{L}()$ is the Lagrange Interpolation function that takes a list of points and returns the polynomial that passes through these points (with the smallest degeree).


### Calculating $La$, $Ra$, and $Oa$ using the polynomials


Now that we have the polynomials representing the matrices, we can calculate $La$, $Ra$, and $Oa$ as following:

$$ La = \left[\begin{array}{cccc} u_1(1) & u_2(1) & u_3(1) & u_4(1) \\
u_1(2) & u_2(2) & u_3(2) & u_4(2) \\
u_1(3) & u_2(3) & u_3(3) & u_4(3) \\
u_1(4) & u_2(4) & u_3(4) & u_4(4)
\end{array} \right] 
\cdot 
\left[ \begin{array}{c} a_1 \\
a_2 \\
a_3 \\
a_4
\end{array} \right] = \left[ u_1(x) \quad u_2(x) \quad u_3(x) \quad u_4(x) \right] \cdot 
\left[ \begin{array}{c} a_1 \\
a_2 \\
a_3 \\
a_4
\end{array} \right] = \sum_{i=1}^4 u_i(x) a_i = u(x) $$

$$ Ra = \left[\begin{array}{cccc} v_1(1) & v_2(1) & v_3(1) & v_4(1) \\
v_1(2) & v_2(2) & v_3(2) & v_4(2) \\
v_1(3) & v_2(3) & v_3(3) & v_4(3) \\
v_1(4) & v_2(4) & v_3(4) & v_4(4)
\end{array} \right] 
\cdot 
\left[ \begin{array}{c} a_1 \\
a_2 \\
a_3 \\
a_4
\end{array} \right] = \left[ v_1(x) \quad v_2(x) \quad v_3(x) \quad v_4(x) \right] \cdot 
\left[ \begin{array}{c} a_1 \\
a_2 \\
a_3 \\
a_4
\end{array} \right] = \sum_{i=1}^4 v_i(x) a_i = v(x) $$


$$ Oa = \left[\begin{array}{cccc} w_1(1) & w_2(1) & w_3(1) & w_4(1) \\
w_1(2) & w_2(2) & w_3(2) & w_4(2) \\
w_1(3) & w_2(3) & w_3(3) & w_4(3) \\
w_1(4) & w_2(4) & w_3(4) & w_4(4)
\end{array} \right] 
\cdot 
\left[ \begin{array}{c} a_1 \\
a_2 \\
a_3 \\
a_4
\end{array} \right] = \left[ w_1(x) \quad w_2(x) \quad w_3(x) \quad w_4(x) \right] \cdot 
\left[ \begin{array}{c} a_1 \\
a_2 \\
a_3 \\
a_4
\end{array} \right] = \sum_{i=1}^4 w_i(x) a_i = w(x) $$


where $a = [a_1, a_2, a_3, a_4]$ is the witness vector.


### Verifying the R1CS constraints using the polynomials


Verifying that $La \odot Ra = Oa$ is now done by checking that


$$
u(x) \cdot v(x) = w(x)
$$


 for a random point $x = r$.


but there is a problem, even if $u(x) \cdot v(x)$ and $w(x)$ interpolate the same points, they might not be equivalent polynomials, so we need to fix this.


How? by introducing the balancing technique. We know that $u(x) \cdot v(x) = w(x) + 0$, so we will introduce a new polynomial $b(x)$ that will be $0$ at all the interpolation points.
The point of it? so the polynomials  $u(x) \cdot v(x)$ and $w(x) + b(x)$ are equivalent.


**IMPORTANT NOTE:** The calculations that are explained so far, and will be explained, are done by the prover.


So now the prover must also calculate $b(x)$ and provide it to the verifier, but how do we force the prover to give a polynomial $b(x)$ that is $0$ at all the interpolation points?
Simply by not asking the prover to provide it :), instead, we will ask the prover to provide us with the polynomial $h(x)$ such that:


$$
b(x) = h(x) \cdot t(x) \implies h(x) = \frac{b(x)}{t(x)}
$$


where $t(x)$ is the target polynomial that has roots at all the interpolation points, meaning:


$$
t(x) = (x-1)(x-2)(x-3)(x-4)
$$


and because the goal is to make the constraint


$$
u(x) \cdot v(x) = w(x) + b(x)
$$


 holds true, the prover can calculate $h(x)$ as following:


$$
h(x) = \frac{u(x) \cdot v(x) - w(x)}{t(x)}
$$


So now the verifier will check that:


$$
u(\tau) \cdot v(\tau) = w(\tau) + h(\tau) \cdot t(\tau)
$$


for a random point $\tau$.


### Our somewhat ZK proof is now succinct and represented using QAP


So finally, our succinct ZK proof using QAP is as following:


$$
\sum_{i=1}^{n} u_i(\tau) \cdot a_i \odot \sum_{i=1}^{n} v_i(\tau) \cdot a_i = \sum_{i=1}^{n} w_i(\tau) \cdot a_i + h(\tau) \cdot t(\tau)
$$


Where $\tau$ is a random selected point, and sent securely to the prover.


So like this, the prover will calculate:


$$
A = u(\tau) = \sum_{i=1}^{n} u_i(\tau) \cdot a_i
$$


$$
B = v(\tau) = \sum_{i=1}^{n} v_i(\tau) \cdot a_i
$$


$$
C = w(\tau) + h(\tau)t(\tau) = \sum_{i=1}^{n} w_i(\tau) \cdot a_i + h(\tau) \cdot t(\tau)
$$


And then the verifier will check that:


$$
A \odot B = C
$$


All of this wthout revealing any information about the witness $a$ to the verifier.


### what needs to be done next


* How do we know that the prover calculated $A$, $B$, and $C$ correctly without revealing the witness?
* Who and how generates $\tau$ securely?


With these limitations, we will hold at the point where the prover calculates $A$, $B$, and $C$, the rest will come in the next step.


## Step 4 (implementation at [917c640](https://github.com/FaresMezenner/groth16-from-scratch/commit/917c640c7b3816ea74d81b2ed029cb73e731fe21)): Trusted Setup for secure values generation


To avoid melicious behavior from the prover, we need to make sure that the values they use to calculate $A$, $B$, and $C$ are generated securely and in a truly random way, so they cannot predict them and use them to cheat.
How can we asssure this? by introducing a third actor in the protocol, called the **Trusted Setup**.


The job of the Trusted Setup, so far, is to generate the random value $\tau$ securely, and also generate some other values that will help the prover to calculate $A$, $B$, and $C$ without revealing the witness (We will see them later).


**Context:** We turned our R1CS into QAP polynomials, so we want to evaluate them at a random point $\tau$ in ECC encrypted domain, so the prover will not reveal the witness values to the verifier, because if the verifier knows $\tau$ or the evaluation is not encrypted, they could brute-force the witness values.


### Structured Reference String (SRS) generation


We know that a polynomial of degree $d$ is the set of coefficients $[c_0, c_1, c_2, ..., c_d]$, and evaluating it at a point $x = r$ is done by calculating the vector multiplication:


$$
\left[ c_0 \quad c_1 \quad c_2 \quad c_3 \quad \ldots \quad c_d \right]
\cdot
\left[
\begin{array}{c}
1 \\
r \\
r^2 \\
r^3 \\
\vdots \\
r^d
\end{array}
\right]
= \sum_{i=0}^d c_i \cdot r^i
$$



so if we want to evaluate a polynomial at a point $\tau$ in ECC encrypted domain, we need to have the values of $[1 \cdot G, \tau \cdot G, \tau^2 \cdot G, \tau^3 \cdot G, ..., \tau^d \cdot G]$, where $G$ is the generator point of the ECC group we are working with, and the result will be as following:


$$
\left[ c_0 \quad c_1 \quad c_2 \quad c_3 \quad \ldots \quad c_d \right]
\cdot
\left[
\begin{array}{c}
1 \cdot G \\
\tau \cdot G \\
\tau^2 \cdot G \\
\tau^3 \cdot G \\
\vdots \\
\tau^d \cdot G
\end{array}
\right]
= \sum_{i=0}^d c_i \cdot (\tau^i \cdot G)
$$



Notice how like this, the result is also in the ECC encrypted domain, because it is a sum of points in the ECC curve, and also, we having that vector of encrypted powers of $\tau$ was enough to evaluate the polynomial at point $\tau$ without knowing $\tau$ itself, and that's exactly what we want.


**Trusted Setup** will generate these values for us, but not only that, it will also generate other values that will help us to evaluate the polynomials $u_i(x)$, $v_i(x)$, and $w_i(x)$ at point $\tau$ in ECC encrypted domain. And since we trust the Trusted Setup, we will assume that it generates these values correctly and securely, does not give $\tau$ to anyone, and deletes it after the generation. In a real-world scenario, the Trusted Setup is done using multi-party computation (MPC) to avoid having to trust a single party, where $\tau$ is mixed with other random values from other parties, so even if one party is melicious, the final $\tau$ will still be secure.


The vector of such values (encrypted powers of a secret value) is called the **Structured Reference String (SRS)**, and it is defined as following for $\tau$:


$$
SRS1 = [G_1, \tau \cdot G_1, \tau^2 \cdot G_1, \tau^3 \cdot G_1, ..., \tau^d \cdot G_1] = [G_1, \Omega_{1}, \Omega_{2}, \Omega_{3}, ..., \Omega_{d}]
$$


$$
SRS2 = [G_2, \tau \cdot G_2, \tau^2 \cdot G_2, \tau^3 \cdot G_2, ..., \tau^d \cdot G_2] = [G_2, \Theta_{1}, \Theta_{2}, \Theta_{3}, ..., \Theta_{d}]
$$


where $d$ is the maximum degree of the polynomials we want to evaluate, in our case it will be $n-1$ where $n$ is the number of constraints, because the degree of the polynomials $u_i(x)$, $v_i(x)$, and $w_i(x)$ is at most $n-1$.


We could verify that the Trusted Setup generated the SRS correctly by checking that:


$$
e(\Theta_{1}, \Omega_{i}) = e(G_2, \Omega_{i+1}) \quad \forall i \in [1, d[
$$


if the trusted setup generates just SRS1, it should also $\Theta_{1} = \tau \cdot G_2$ securely, to verify that the SRS1 is generated correctly by checking the above.
And the same logic applies if it generates just SRS2.


### The needed SRS for our ZK proof


We defined $SRS1$ and $SRS2$ for $\tau$, they are needed to evaluate the polynomials $u_i(x)$, $w_i() and $v_i(x)$ at point $\tau$ in ECC encrypted domain (respectively).


But what about evaluating $h(x)t(x)$ at point $\tau$ in ECC encrypted domain? First you need to know that the degree of this polynomial is:


$$
(n-2) + n = 2n-2
$$


So the existing SRSs are none use.
Also know that we can't evaluate $h(\tau)$ and $t(\tau)$ separately, because then we can't get an $\mathbb{G}_1$ element as a result.


Our solution? The Trusted Setup will evaluate $t(x)$ at point $\tau$ directly in ECC encrypted domain, and then multiply it by the powers of $\tau$ to get the needed SRS:


$$
SRS3 = [t(\tau)G_1, \tau t(\tau) G_1, \tau^2 t(\tau) G_1, \tau^3 t(\tau) G_1, ..., \tau^{n-2} t(\tau) G_1] = [\Upsilon_{0}, \Upsilon_{1}, \Upsilon_{2}, \Upsilon_{3}, ..., \Upsilon_{n-2}]
$$


Then we will use this to evalute $h(x)t(\tau)$ at point $\tau$ in ECC encrypted domain, beacause, which is equal to evaluating $h(x)t(x)$ at point $\tau$ directly.


### All what's left is to check


Since we have all the needed SRSs to evaluate all the polynomials, the prover can calculate $A$, $B$ and $C$, then the verifier will check directly that this equation is balanced:


$$
A \cdot B = C \cdot G_2
$$


Which balances out if the prover has a witness that satisfies the QAP constraints.


Where all the values are in ECC encrypted domain, so the verifier does not learn anything about the witness values.
And we could notice that no matter how big our R1CS is, the proof size is always $256 bytes$ large (if we consider that $\mathbb{G}_1$ elements are $64 bytes$ large, and $\mathbb{G}_2$ elements are $128 bytes$ large), and the verification time is constant as well, which makes our ZK proof succinct.


### What needs to be done next


* The prover can still provide arbitrary values for $A$, $B$, and $C$, so the equation balances out even if they do not have a valid witness, how can we fix this?


## Step 5 (Completed): Making our proof sound (resilient to melicious provers)


We've said that the prover could choose arbitrary values for $A$, $B$, and $C$ such that the equation balances out, simply by choosing simple values on the finite field, $a$, $b$, and $c$, such that $ab = c$, and then setting:


$$
A = a \cdot G_1
$$


$$
B = b \cdot G_2
$$


$$
C = c \cdot G_1
$$


this will make the equation balance out, because:


$$
e(A, B) = e(a \cdot G_1, b \cdot G_2) \iff e(G_1, G_2)^{ab} = e(G_1, G_2)^{c} \iff ab = c
$$


### Introducing $\alpha$ and $\beta$


This values will be generated by the Trusted Setup, where:


$$
\alpha \text{ is a scalar and } \alpha \cdot G_1 = [\alpha]_{1} \in \mathbb{G}_1
$$


$$
\beta \text{ is a scalar and } \beta \cdot G_2 = [\beta]_{2} \in \mathbb{G}_2
$$


and then published to be used to calculate $D = [\alpha]_{1} \cdot \beta$, a new value that will be sent by the prover along with $A$, $B$, and $C$.


Why do we do this? because our new QAP equation will be:


$$
A \cdot B = D + C \cdot G_2 = [\alpha]_{1} \cdot [\beta]_{2}  + C \cdot G_2
$$


It's obvious that $D \in \mathbb{G}_T$, because it is the result of pairing $[\alpha]_{1}$ and $[\beta]_{2}$.


Why do we need this? because the user cannot find $a$, $b$, and $c$ such that:


$$
e(a \cdot G_1, b \cdot G_2) = e([\alpha]_{1}, [\beta]_{2}) + e(c \cdot G_1, G_2)
$$


But how can we add these values to the equation without breaking it? by changing the way we calculate $A$, $B$, and $C$ as following:

$$
\left( [\alpha]_{1} + \sum_{i=1}^{m} a_i u_i(\tau) \right)_A \cdot \left( [\beta]_{2} + \sum_{i=1}^{m} a_i v_i(\tau) \right)_B = [\alpha]_{1} \bullet [\beta]_{2} + \left( \alpha \sum_{i=1}^{m} a_i v_i(\tau) + \beta \sum_{i=1}^{m} a_i u_i(\tau) + \sum_{i=1}^{m} a_i w_i(\tau) + h(\tau) t(\tau) \right)_C \bullet G_2
$$

The prover can and will calculate \(A\), \(B\), but for \(C\), it's a problem, they do not know \(\alpha\) and \(\beta\) scalars, so how can they calculate it?
The answer is simple, the Trusted Setup will step in again, by calculating and providing the values of the problematic part of \(C\):

$$
\alpha \sum_{i=1}^{m} a_i v_i(\tau) + \beta \sum_{i=1}^{m} a_i u_i(\tau) + \sum_{i=1}^{m} a_i w_i(\tau) = \sum_{i=1}^{m} a_i\,\boxed{\left( \alpha v_i(\tau) + \beta u_i(\tau) + w_i(\tau) \right)}
$$

Only the boxed part is provided by the Trusted Setup to the prover, because it is the problematic part for the prover to calculate (the \(a_i\) are known by the prover).

These values will be provided in a \(\Psi\) vector as:

$$
\Psi_i = (\alpha v_i(\tau) + \beta u_i(\tau) + w_i(\tau)) \cdot G_1 \quad \forall i \in [1, m]
$$

With this, the prover calculates \(C\) as:

$$
C = \left( \sum_{i=1}^m a_i \Psi_i + h(\tau) t(\tau) \right)
$$

At this point, the way to calculate \(h(x)\) does not change despite the modified QAP equation.

---

### Introducing $\delta$ and $\gamma$

To verify \(A\), \(B\), and \(C\) correctly, the verifier needs access to the first \(l\) values of the witness \(a = [a_1, ..., a_m]\), corresponding to public inputs.

The verifier separates public and private inputs:

$$
A \cdot B = [\alpha]_1 \cdot [\beta]_2 + \sum_{i=0}^l a_i \psi_i + \left( \sum_{i=l+1}^m a_i \psi_i + h(\tau) t(\tau) \right)_C \cdot G_2
$$

Verification equation:

$$
A \cdot B = [\alpha]_1 \cdot [\beta]_2 + [X]_1 \cdot G_2 + C \cdot G_2
$$

where

$$
[X]_1 = \sum_{i=0}^l a_i \psi_i
$$

---

A malicious prover could cheat by declaring incorrect public inputs, so to separate public and private inputs securely:

$$
\delta \text{ is a scalar and } \delta \cdot G_1 = [\delta]_1 \in \mathbb{G}_1
$$

$$
\gamma \text{ is a scalar and } \gamma \cdot G_2 = [\gamma]_2 \in \mathbb{G}_2
$$

$\Psi_i$ from Trusted Setup is set as:

$$
\Psi_i = \begin{cases}
\frac{(\alpha v_i(\tau) + \beta u_i(\tau) + w_i(\tau))}{\gamma} \cdot G_1 & \text{if } i \leq l \\
\frac{(\alpha v_i(\tau) + \beta u_i(\tau) + w_i(\tau))}{\delta} \cdot G_1 & \text{if } i > l
\end{cases}
$$

Trusted Setup also provides:

$$
SRS3 = \left[ \frac{t(\tau)}{\delta}G_1, \frac{\tau t(\tau)}{\delta} G_1, \frac{\tau^2 t(\tau)}{\delta} G_1, ..., \frac{\tau^{n-2} t(\tau)}{\delta} G_1 \right] = [\Upsilon_0, \Upsilon_1, ..., \Upsilon_{n-2}]
$$

The new QAP equation is:

$$
A \cdot B = [\alpha]_1 \cdot [\beta]_2 + [X]_1 \cdot [\gamma]_2 + C \cdot [\delta]_2
$$

---

### Salting the proof with random scalars \(r\) and \(s\):

$$
[A]_1 = [\alpha]_1 + \sum_{i=1}^m a_i u_i(\tau) + r [\delta]_1
$$

$$
[B]_2 = [\beta]_2 + \sum_{i=1}^m a_i v_i(\tau) + s [\delta]_2
$$

$$
[B]_1 = [\beta]_1 + \sum_{i=1}^m a_i v_i(\tau) + s [\delta]_1
$$

$$
[C]_1 = \sum_{i=\ell+1}^m a_i [\Psi_i]_1 + h(\tau) t(\tau) + A s + B r - r s [\delta]_1
$$

Defining:

$$
\underbrace{\left( \alpha + \sum_{i=1}^m a_i u_i(x) + r \delta \right)}_A \times \underbrace{\left( \beta + \sum_{i=1}^m a_i v_i(x) + s \delta \right)}_B
$$

The final QAP equation:

$$
\underbrace{\left( \alpha + \sum_{i=1}^m a_i u_i(x) + r \delta \right)}_{[A]_1} \times \underbrace{\left( \beta + \sum_{i=1}^m a_i v_i(x) + s \delta \right)}_{[B]_2} 
= \boxed{\alpha \beta} + \boxed{\gamma} + \boxed{\frac{\sum_{i=1}^\ell a_i ( \alpha v_i(x) + \beta u_i(x) + w_i(x) )}{\gamma}} + \underbrace{\boxed{\delta} \frac{\sum_{i=\ell+1}^m a_i ( \alpha v_i(x) + \beta u_i(x) + w_i(x) ) + h(x) t(x)}{\delta} + A s + B r - r s \delta}_{[C]_1} $$

**Note:** \([A]_1\), \([B]_2\), and \([C]_1\) are values in ECC encrypted domain, i.e., points encrypting \(A\), \(B\), and \(C\) respectively.


## What now?


The proof is sound, succinct, and zero-knowledge, but there are still some optimizations to make, so it becomes either faster or more secure.
For example, Groth16 is Malleable, meaning that an attacker could change a valid proof to another valid proof without knowing the witness, such attack has a proof of concept demonstrated in this [article](https://medium.com/@cryptofairy/exploring-vulnerabilities-the-zksnark-malleability-attack-on-the-groth16-protocol-8c80d13751c5)





