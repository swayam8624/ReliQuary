pragma circom 2.0.0; // <--- Remove the period from this line

template Multiplier2() {
    signal input a;
    signal input b;
    signal output c;

    c <== a * b;
}

component main = Multiplier2();