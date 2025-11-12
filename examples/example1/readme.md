# Example 1: The prover tries to prove that he has a number that is larger than 8 without revealing anything else

## Defining the circuit

Our circuit will have the following input wires:

- $a_0, a_1, a_2, a_3$: the bits of the number in binary (4 bits, so max number is 15).
- $v$: the actual number in decimal representation.

so to check if the number is larger than 8, we need to check if $a_3$ (the most significant bit) is equal to $1$.
and of course, we need to make sure that the bits are binary (0 or 1) and that they correspond to the decimal number $v$.

so our circuit will have the following gates:
$$
\text{Check bits are binary: } 0 = a_i \cdot (a_i - 1)  \text{ for } i=0,1,2,3 or \text{ in other words } 0 = a_i \cdot a_i - a_i
\text{Checks decimal representation: } v = a_0 \cdot 1 + a_1 \cdot 2 + a_2 \cdot 4 + a_3 \cdot 8
\text{Check most significant bit is 1: } 1 = a_3
$$

## R1CS representation

First we re define the constraints in a more R1CS friendly way:

- For each bit $a_i$ (where $i=0,1,2,3$), we have the constraint:

$$
a_i = a_i \cdot a_i
$$

- For the decimal representation, we have the constraint:

$$
v - a_0 \cdot 1 - a_1 \cdot 2 - a_2 \cdot 4 - a_3 \cdot 8 = 0
$$

- For the most significant bit check, we have the constraint:

$$
1 - a_3 = 0
$$

The witness vector will be:
$$
a = [1, a_0=0, a_1=1, a_2=1, a_3=1, v=14]
$$

Now for the R1CS matrices L, R, O, we have 6 constraints (4 for the bits, 1 for the decimal representation, and 1 for the most significant bit check) and 6 wires (the constant wire, the 4 bits, and the decimal number).

$$
L = \begin{bmatrix}
0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0
\end{bmatrix}
\qquad
R = \begin{bmatrix}
0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0
\end{bmatrix}
\qquad
O = \begin{bmatrix}
0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 \\
0 & -1 & -2 & -4 & -8 & 1 \\
1 & 0 & 0 & 0 & -1 & 0
\end{bmatrix}
$$
